"""Local-only API process used by the no-mock web vertical E2E."""
from pathlib import Path
import sys
import asyncio
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from hard_api.backup.service import LocalBackupService
from hard_api.core.config import Settings
from hard_api.db import migrations
from hard_api.main import create_app

run_id = os.environ.get("HARD_E2E_RUN_ID")
if not run_id:
    raise RuntimeError("HARD_E2E_RUN_ID is required for isolated E2E data.")
temporary = ROOT / ".tool-cache" / f"live-e2e-{run_id}"
applications: dict[str, object] = {}


def application_for(client: str) -> object:
    if client not in {"default", "desktop", "mobile"}:
        raise ValueError("invalid isolated E2E client")
    application = applications.get(client)
    if application is not None:
        return application
    workspace = temporary / client
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

if __name__ == "__main__":
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None: pass
        def _handle(self) -> None:
            length = int(self.headers.get("content-length", "0"))
            body = self.rfile.read(length)
            messages: list[dict[str, object]] = []
            async def receive() -> dict[str, object]: return {"type": "http.request", "body": body, "more_body": False}
            async def send(message: dict[str, object]) -> None: messages.append(message)
            scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": self.command, "scheme": "http", "path": self.path.split("?", 1)[0], "raw_path": self.path.split("?", 1)[0].encode(), "query_string": self.path.partition("?")[2].encode(), "headers": [(key.lower().encode(), value.encode()) for key, value in self.headers.items()], "client": ("127.0.0.1", 0), "server": ("127.0.0.1", 8000), "root_path": ""}
            try:
                client = self.headers.get("X-Hard-E2E-Client", "default")
                asyncio.run(application_for(client)(scope, receive, send))
            except ValueError:
                self.send_response(400)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"detail":"invalid isolated E2E client"}')
                return
            start = next(message for message in messages if message["type"] == "http.response.start")
            self.send_response(int(start["status"]))
            for key, value in start.get("headers", []): self.send_header(bytes(key).decode(), bytes(value).decode())
            self.end_headers()
            self.wfile.write(b"".join(bytes(message.get("body", b"")) for message in messages if message["type"] == "http.response.body"))
        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _handle
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
