from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from hard_api.backup.service import LocalBackupService
from hard_api.db import migrations
from hard_api.main import create_app
from test_catalog import make_settings, write_python_fixture


def test_backup_api_exports_downloads_and_imports_a_user_selected_archive_from_memory(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    settings = make_settings(content_root)
    service = LocalBackupService(settings.backup_dir, today=lambda: date(2026, 8, 25))
    migrations.migrate_database(settings.database_path, backup_provider=service)
    with closing(sqlite3.connect(settings.database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES ('restore-me', 'before-export', CURRENT_TIMESTAMP)"
            )
    app = create_app(settings)
    app.state.backup_service = service

    with TestClient(app) as client:
        exported = client.post("/api/backup/export", headers={"Idempotency-Key": "export-1"})
        assert exported.status_code == 200
        archive_name = exported.json()["archive_name"]
        export_replay = client.post("/api/backup/export", headers={"Idempotency-Key": "export-1"})
        assert export_replay.json()["archive_name"] == archive_name
        archive_bytes = (settings.export_dir / archive_name).read_bytes()
        with closing(sqlite3.connect(settings.database_path)) as connection:
            with connection:
                connection.execute("UPDATE settings SET value = 'current' WHERE key = 'restore-me'")
        restored = client.post(
            "/api/backup/import",
            content=archive_bytes,
            headers={"X-Archive-Name": archive_name, "Idempotency-Key": "import-1"},
        )
        unsafe = client.post(
            "/api/backup/import",
            content=b"archive",
            headers={"X-Archive-Name": "../unsafe.zip", "Idempotency-Key": "import-unsafe"},
        )

    assert restored.status_code == 200
    assert len(list(settings.export_dir.glob("*.zip"))) == 1
    assert unsafe.status_code == 400
    assert unsafe.json()["error"]["code"] == "invalid_archive_name"
    with closing(sqlite3.connect(settings.database_path)) as connection:
        assert connection.execute("SELECT value FROM settings WHERE key = 'restore-me'").fetchone() == ("before-export",)
