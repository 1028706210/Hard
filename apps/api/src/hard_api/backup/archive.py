from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from typing import Mapping
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile


ARCHIVE_FORMAT_VERSION = 1
_DATABASE_NAME = "database.sqlite"
_SETTINGS_NAME = "settings.json"
_CONTENT_VERSION_NAME = "content-version.json"
_MANIFEST_NAME = "manifest.json"
_PAYLOAD_NAMES = (_DATABASE_NAME, _SETTINGS_NAME, _CONTENT_VERSION_NAME)
_ALLOWED_NAMES = frozenset((*_PAYLOAD_NAMES, _MANIFEST_NAME))
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 32 * 1024 * 1024


class ArchiveError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ArchiveContents:
    database_bytes: bytes
    settings_manifest: dict[str, object]
    content_version: str


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def _unsafe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return not name or "\\" in name or path.is_absolute() or ".." in path.parts or ":" in name


def create_archive(
    database_path: Path,
    destination: Path,
    *,
    settings_manifest: Mapping[str, object],
    content_version: str,
) -> Path:
    database_bytes = database_path.read_bytes()
    settings_bytes = _canonical_json(dict(settings_manifest))
    content_bytes = _canonical_json({"content_version": content_version})
    payload = {
        _DATABASE_NAME: database_bytes,
        _SETTINGS_NAME: settings_bytes,
        _CONTENT_VERSION_NAME: content_bytes,
    }
    manifest = {
        "format_version": ARCHIVE_FORMAT_VERSION,
        "files": [{"path": name, "sha256": _digest(payload[name])} for name in _PAYLOAD_NAMES],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
            for name in _PAYLOAD_NAMES:
                archive.writestr(name, payload[name])
            archive.writestr(_MANIFEST_NAME, _canonical_json(manifest))
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def _load_manifest(value: bytes) -> dict[str, object]:
    try:
        manifest = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArchiveError("归档清单无效。") from error
    if not isinstance(manifest, dict) or manifest.get("format_version") != ARCHIVE_FORMAT_VERSION:
        raise ArchiveError("归档版本不兼容。")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ArchiveError("归档清单无效。")
    expected = {record["path"]: record.get("sha256") for record in files if isinstance(record, dict) and isinstance(record.get("path"), str)}
    if set(expected) != set(_PAYLOAD_NAMES) or len(expected) != len(files):
        raise ArchiveError("归档清单文件不完整。")
    if any(not isinstance(value, str) or len(value) != 64 for value in expected.values()):
        raise ArchiveError("归档校验和无效。")
    return expected


def inspect_archive(archive_path: Path) -> ArchiveContents:
    try:
        if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
            raise ArchiveError("归档体积超过限制。")
        with ZipFile(archive_path) as archive:
            if sum(entry.file_size for entry in archive.infolist()) > MAX_UNCOMPRESSED_BYTES:
                raise ArchiveError("归档解压体积超过限制。")
            names = [entry.filename for entry in archive.infolist()]
            if any(_unsafe_name(name) for name in names):
                raise ArchiveError("归档路径不安全。")
            if len(names) != len(set(names)):
                raise ArchiveError("归档包含重复文件。")
            if set(names) != _ALLOWED_NAMES:
                raise ArchiveError("归档包含未允许的文件。")
            payload = {name: archive.read(name) for name in _PAYLOAD_NAMES}
            expected = _load_manifest(archive.read(_MANIFEST_NAME))
    except ArchiveError:
        raise
    except (OSError, ValueError) as error:
        raise ArchiveError("无法读取归档。") from error
    for name in _PAYLOAD_NAMES:
        if _digest(payload[name]) != expected[name]:
            raise ArchiveError("归档校验失败。")
    try:
        settings_manifest = json.loads(payload[_SETTINGS_NAME].decode("utf-8"))
        content_manifest = json.loads(payload[_CONTENT_VERSION_NAME].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArchiveError("归档元数据无效。") from error
    if not isinstance(settings_manifest, dict) or not isinstance(content_manifest, dict):
        raise ArchiveError("归档元数据无效。")
    content_version = content_manifest.get("content_version")
    if not isinstance(content_version, str):
        raise ArchiveError("归档内容版本无效。")
    return ArchiveContents(
        database_bytes=payload[_DATABASE_NAME],
        settings_manifest=settings_manifest,
        content_version=content_version,
    )
