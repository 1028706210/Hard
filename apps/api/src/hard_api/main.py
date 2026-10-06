from __future__ import annotations

from contextlib import closing
import sqlite3
import threading
import asyncio
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from hard_api.api.content import router as content_router
from hard_api.api.health import router as health_router
from hard_api.api.assessment import router as assessment_router
from hard_api.api.growth import router as growth_router
from hard_api.api.progress import router as progress_router
from hard_api.api.search import router as search_router
from hard_api.api.review import router as review_router
from hard_api.api.runners import router as runners_router
from hard_api.api.backup import router as backup_router
from hard_api.backup.service import LocalBackupService
from hard_api.api.lan import router as lan_router
from hard_api.core.network import LanAccessController, NetworkConfigurationError
from hard_api.content.repository import ContentRepository
from hard_api.content.service import ContentService
from hard_api.core.config import Settings
from hard_api.core.errors import (
    ApiError,
    api_error_handler,
    http_error_handler,
    unhandled_error_handler,
)
from hard_api.core.logging import configure_logging
from hard_api.search.service import SearchService
from hard_api.runners.manager import RunManager
from hard_api.runners.python import PythonRunner


class _UvicornLanLauncher:
    def __init__(self, app: FastAPI, *, frontend_root: Path | None = None) -> None:
        self.app = app
        self.frontend_root = frontend_root or app.state.settings.project_root / "apps" / "web" / "dist"
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None
    def start(self, host: str, port: int) -> None:
        if self.thread is not None and self.thread.is_alive(): return
        application = self.app
        frontend_root = self.frontend_root.resolve()
        shell_path = frontend_root / "index.html"
        if not shell_path.is_file():
            raise NetworkConfigurationError(
                "lan_frontend_build_required",
                "需要先构建 Hard 前端：pnpm --dir apps/web build。",
            )

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None: pass
            def _send_static(self, path: str) -> bool:
                relative = path.lstrip("/")
                if not relative.startswith("assets/"):
                    return False
                candidate = (frontend_root / relative).resolve()
                try:
                    candidate.relative_to(frontend_root)
                except ValueError:
                    self.send_error(404)
                    return True
                if not candidate.is_file():
                    self.send_error(404)
                    return True
                self.send_response(200)
                self.send_header("content-type", mimetypes.guess_type(candidate.name)[0] or "application/octet-stream")
                self.end_headers()
                self.wfile.write(candidate.read_bytes())
                return True
            def _handle(self) -> None:
                request_path = unquote(urlsplit(self.path).path)
                if not request_path.startswith("/api/"):
                    if self._send_static(request_path):
                        return
                    self.send_response(200)
                    self.send_header("content-type", "text/html; charset=utf-8")
                    self.end_headers(); self.wfile.write(shell_path.read_bytes())
                    return
                body = self.rfile.read(int(self.headers.get("content-length", "0")))
                messages: list[dict[str, object]] = []
                async def receive() -> dict[str, object]: return {"type": "http.request", "body": body, "more_body": False}
                async def send(message: dict[str, object]) -> None: messages.append(message)
                scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": self.command, "scheme": "http", "path": self.path.split("?", 1)[0], "raw_path": self.path.split("?", 1)[0].encode(), "query_string": self.path.partition("?")[2].encode(), "headers": [(key.lower().encode(), value.encode()) for key, value in self.headers.items()], "client": (host, 0), "server": (host, port), "root_path": ""}
                asyncio.run(application(scope, receive, send))
                start = next(message for message in messages if message["type"] == "http.response.start")
                self.send_response(int(start["status"]))
                for key, value in start.get("headers", []): self.send_header(bytes(key).decode(), bytes(value).decode())
                self.end_headers(); self.wfile.write(b"".join(bytes(message.get("body", b"")) for message in messages if message["type"] == "http.response.body"))
            do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _handle
        self.server = ThreadingHTTPServer((host, port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="hard-lan")
        self.thread.start()
    def stop(self) -> None:
        if self.server is not None: self.server.shutdown(); self.server.server_close()
        if self.thread is not None: self.thread.join(timeout=5)
        self.server = None; self.thread = None


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    app = FastAPI(title="Hard API", version="0.1.0")
    app.state.settings = settings or Settings.from_environment()
    content_repository = ContentRepository(app.state.settings.content_dir)
    app.state.content_service = ContentService(content_repository)
    app.state.search_service = SearchService(app.state.settings.database_path, content_repository)
    app.state.runner_manager = RunManager(
        app.state.settings.runner_work_dir,
        adapters={"python": PythonRunner()},
        protected_paths=(app.state.settings.data_dir, app.state.settings.backup_dir, app.state.settings.export_dir),
    )
    app.state.backup_service = LocalBackupService(app.state.settings.backup_dir)
    app.state.lan_controller = LanAccessController(launcher=_UvicornLanLauncher(app))

    @app.on_event("shutdown")
    def stop_local_services() -> None:
        app.state.lan_controller.disable()
        app.state.runner_manager.shutdown()

    def is_learning_write(request: Request) -> bool:
        return (
            request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and request.url.path.startswith(("/api/progress/", "/api/assessment/", "/api/review/"))
        )

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        request.state.request_id = request_id
        if not is_learning_write(request):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        with closing(sqlite3.connect(app.state.settings.database_path)) as observer:
            before = observer.execute("PRAGMA data_version").fetchone()
            response = await call_next(request)
            changed = observer.execute("PRAGMA data_version").fetchone() != before
        if 200 <= response.status_code < 300 and changed:
            app.state.backup_service.backup_after_successful_learning_write(
                app.state.settings.database_path
            )
        response.headers["X-Request-ID"] = request_id
        return response

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    app.include_router(health_router)
    app.include_router(content_router)
    app.include_router(assessment_router)
    app.include_router(growth_router)
    app.include_router(progress_router)
    app.include_router(search_router)
    app.include_router(review_router)
    app.include_router(runners_router)
    app.include_router(backup_router)
    app.include_router(lan_router)
    return app


app = create_app()
