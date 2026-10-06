from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel

from hard_api.backup.archive import ArchiveError, MAX_ARCHIVE_BYTES
from hard_api.core.errors import ApiError


router = APIRouter(prefix="/api/backup", tags=["backup"])


def _response(title: str) -> dict[int, dict[str, object]]:
    return {200: {"content": {"application/json": {"schema": {"type": "object", "title": title, "additionalProperties": True}}}}}


class ExportResponse(BaseModel):
    archive_name: str
    content_version: str


class ImportResponse(BaseModel):
    content_version: str


def _archive_path(request: Request, archive_name: str) -> Path:
    candidate = Path(archive_name)
    if candidate.name != archive_name or candidate.suffix.lower() != ".zip":
        raise ApiError("invalid_archive_name", "归档名称不合法。")
    root = request.app.state.settings.export_dir.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ApiError("invalid_archive_name", "归档名称不合法。") from error
    return resolved


def _require_key(value: str | None) -> str:
    if value is None or not 1 <= len(value) <= 128:
        raise ApiError("invalid_idempotency_key", "幂等键不合法。")
    return value


@router.post("/export", response_model=ExportResponse, responses=_response("ExportResponse"))
def export_data(
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, str]:
    key = _require_key(idempotency_key)
    cache = getattr(request.app.state, "backup_export_keys", {})
    if key in cache:
        return cache[key]
    settings = request.app.state.settings
    archive_name = f"hard-export-{sha256(idempotency_key.encode('utf-8')).hexdigest()[:24]}.zip"
    path = _archive_path(request, archive_name)
    exported = request.app.state.backup_service.export_archive(
        settings.database_path,
        path,
        settings_manifest={"format_version": 1, "application": "Hard"},
        content_version=request.app.state.content_service.repository.content_version,
    )
    response = {"archive_name": exported.name, "content_version": request.app.state.content_service.repository.content_version}
    cache[key] = response
    request.app.state.backup_export_keys = cache
    return response


@router.post("/import", response_model=ImportResponse, responses=_response("ImportResponse"))
async def import_data(
    request: Request,
    archive_name: str | None = Header(default=None, alias="X-Archive-Name"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, str]:
    key = _require_key(idempotency_key)
    if archive_name is None:
        raise ApiError("invalid_archive_name", "归档名称不合法。")
    _archive_path(request, archive_name)
    archive_bytes = await request.body()
    if not archive_bytes or len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ApiError("invalid_archive", "归档无法安全导入。")
    fingerprint = sha256(archive_bytes).hexdigest()
    cache = getattr(request.app.state, "backup_import_keys", {})
    existing = cache.get(key)
    if existing is not None:
        if existing[0] != fingerprint:
            raise ApiError("idempotency_conflict", "幂等键不能用于不同的导入归档。", status_code=409)
        return existing[1]
    temporary = request.app.state.settings.backup_dir / f"upload-{uuid4().hex}.zip"
    try:
        temporary.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(archive_bytes)
        result = request.app.state.backup_service.import_archive(
            temporary, request.app.state.settings.database_path
        )
    except (ArchiveError, OSError, RuntimeError) as error:
        raise ApiError("invalid_archive", "归档无法安全导入。") from error
    finally:
        temporary.unlink(missing_ok=True)
    response = {"content_version": result.content_version}
    cache[key] = (fingerprint, response)
    request.app.state.backup_import_keys = cache
    return response
