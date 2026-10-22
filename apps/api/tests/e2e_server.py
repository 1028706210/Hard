"""Local-only, full-lifespan API process for the no-mock web vertical E2E."""
from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
import os
import sys

import uvicorn
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from hard_api.backup.service import LocalBackupService
from hard_api.core.config import Settings
from hard_api.db import migrations
from hard_api.main import create_app

RUN_ID = os.environ.get("HARD_E2E_RUN_ID")
if not RUN_ID:
    raise RuntimeError("HARD_E2E_RUN_ID is required for isolated E2E data.")

WORKSPACE = ROOT / ".tool-cache" / f"live-e2e-{RUN_ID}"
CLIENTS = ("default", "desktop", "mobile")
applications: dict[str, FastAPI] = {}


def application_for(client: str) -> FastAPI:
    if client not in CLIENTS:
        raise ValueError("invalid isolated E2E client")
    application = applications.get(client)
    if application is not None:
        return application

    workspace = WORKSPACE / client
    settings = Settings(
        ROOT,
        workspace / "data",
        workspace / "data" / "hard.db",
        workspace / "backups",
        workspace / "exports",
        workspace / "runner-work",
        ROOT / "content",
        ROOT / "docs" / "setup" / "toolchain-lock.json",
    )
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
    application = create_app(settings)
    applications[client] = application
    return application


@asynccontextmanager
async def full_lifespan(application: FastAPI):
    async with AsyncExitStack() as stack:
        for client in CLIENTS:
            client_application = application_for(client)
            await stack.enter_async_context(client_application.router.lifespan_context(client_application))
        application.state.e2e_lifespan_ready = True
        yield
        application.state.e2e_lifespan_ready = False


control = FastAPI(lifespan=full_lifespan)


@control.get("/_e2e/lifecycle")
def lifecycle() -> dict[str, object]:
    return {
        "lifespan": "started" if control.state.e2e_lifespan_ready else "stopped",
        "clients": list(CLIENTS),
        "application_count": len(applications),
    }


class IsolatedE2EApplication:
    async def __call__(self, scope: dict[str, object], receive: object, send: object) -> None:
        if scope["type"] == "lifespan":
            await control(scope, receive, send)  # type: ignore[arg-type]
            return
        if scope["type"] != "http":
            return

        path = str(scope["path"])
        if path == "/api/_e2e/lifecycle":
            control_scope = {**scope, "path": "/_e2e/lifecycle", "raw_path": b"/_e2e/lifecycle"}
            await control(control_scope, receive, send)  # type: ignore[arg-type]
            return

        headers = dict(scope.get("headers", []))  # type: ignore[arg-type]
        client = headers.get(b"x-hard-e2e-client", b"default").decode("ascii")
        await application_for(client)(scope, receive, send)  # type: ignore[arg-type]


app = IsolatedE2EApplication()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
