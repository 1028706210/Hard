from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request, Response

from hard_api.core.config import Settings
from hard_api.core.readiness import database_checks

router = APIRouter(prefix="/api/v1/health", tags=["health"])

_RUNNERS = {
    "python": "python",
    "java": "java",
    "csharp": "dotnet",
    "cpp": "msys2-gcc",
}


def _runner_checks(lock_path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8-sig"))
        if isinstance(payload, list):
            records = {
                str(record.get("name")): record
                for record in payload
                if isinstance(record, dict) and record.get("name")
            }
    except (OSError, json.JSONDecodeError):
        pass

    checks: dict[str, dict[str, Any]] = {}
    for runner, tool_name in _RUNNERS.items():
        record = records.get(tool_name)
        if record is None:
            checks[runner] = {
                "healthy": False,
                "detail": f"未在工具链锁文件中找到 {tool_name}。",
            }
            continue
        checks[runner] = {
            "healthy": bool(record.get("healthy")),
            "path": record.get("path", ""),
        }
    return checks


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request, response: Response) -> dict[str, Any]:
    settings: Settings = request.app.state.settings
    checks: dict[str, dict[str, Any]] = {
        **database_checks(settings.database_path),
        "content": {
            "healthy": settings.content_dir.is_dir(),
            "path": str(settings.content_dir),
        },
    }
    checks.update(_runner_checks(settings.toolchain_lock_path))
    healthy = all(check["healthy"] for check in checks.values())
    if not healthy:
        response.status_code = 503
    return {"status": "ok" if healthy else "degraded", "checks": checks}
