from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from dataclasses import replace
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content"))

from hard_api.backup.service import LocalBackupService
from hard_api.db import migrations
from hard_api.main import create_app
from test_catalog import make_settings, write_python_fixture


def migrated_database(tmp_path: Path, *, today: date = date(2026, 8, 25)) -> tuple[Path, LocalBackupService]:
    database_path = tmp_path / "data" / "hard.db"
    service = LocalBackupService(tmp_path / "backups", today=lambda: today)
    migrations.migrate_database(database_path, backup_provider=service)
    return database_path, service


def test_daily_backup_checkpoints_wal_copies_committed_data_and_runs_once_per_day(tmp_path: Path) -> None:
    database_path, service = migrated_database(tmp_path)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES ('theme', 'dark', CURRENT_TIMESTAMP)"
            )

    first = service.backup_after_successful_learning_write(database_path)
    second = service.backup_after_successful_learning_write(database_path)

    assert first is not None and first.name == "daily-2026-08-25.db"
    assert second is None
    with closing(sqlite3.connect(first)) as backup:
        assert backup.execute("SELECT value FROM settings WHERE key = 'theme'").fetchone() == ("dark",)
        assert backup.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    assert len(list((tmp_path / "backups").glob("daily-*.db"))) == 1


def test_first_successful_learning_write_uses_the_application_backup_service_once(tmp_path: Path) -> None:
    content_root = tmp_path / "content"
    write_python_fixture(content_root)
    settings = make_settings(content_root)
    service = LocalBackupService(settings.backup_dir, today=lambda: date(2026, 8, 25))
    migrations.migrate_database(settings.database_path, backup_provider=service)
    app = create_app(settings)
    app.state.backup_service = service

    with TestClient(app) as client:
        first = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 1, "time_spent_seconds": 10},
            headers={"Idempotency-Key": "backup-first-write"},
        )
        replay = client.patch(
            "/api/progress/lessons/python-foundations-hello-world",
            json={"position": 1, "time_spent_seconds": 10},
            headers={"Idempotency-Key": "backup-first-write"},
        )

    assert first.status_code == replay.status_code == 200
    assert [path.name for path in settings.backup_dir.glob("daily-*.db")] == ["daily-2026-08-25.db"]


def test_snapshot_provider_restores_pre_migration_data_without_touching_the_real_data_directory(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "temporary" / "hard.db"
    database_path.parent.mkdir(parents=True)
    service = LocalBackupService(tmp_path / "backups", today=lambda: date(2026, 8, 25))
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("CREATE TABLE before_upgrade (value TEXT NOT NULL)")
            connection.execute("INSERT INTO before_upgrade (value) VALUES ('keep')")

    def destructive_upgrade(_configuration, _target_revision: str) -> None:
        with closing(sqlite3.connect(database_path)) as connection:
            with connection:
                connection.execute("DROP TABLE before_upgrade")
        raise RuntimeError("migration failed after a commit")

    monkeypatch.setattr(migrations.command, "upgrade", destructive_upgrade)
    try:
        migrations.migrate_database(database_path, backup_provider=service)
    except RuntimeError as error:
        assert str(error) == "migration failed after a commit"
    else:
        raise AssertionError("the injected migration failure must propagate")

    with closing(sqlite3.connect(database_path)) as connection:
        assert connection.execute("SELECT value FROM before_upgrade").fetchone() == ("keep",)
    assert list((tmp_path / "backups").glob("migration-*.db"))


def test_restore_snapshot_rejects_a_snapshot_path_that_does_not_exist(tmp_path: Path) -> None:
    service = LocalBackupService(tmp_path / "backups")

    with pytest.raises(RuntimeError, match="恢复快照不存在"):
        service.restore_snapshot(tmp_path / "missing.db", tmp_path / "data" / "hard.db")


def test_daily_backup_preserves_an_existing_weekly_checkpoint(tmp_path: Path) -> None:
    backup_day = date(2026, 8, 25)
    database_path = tmp_path / "data" / "hard.db"
    service = LocalBackupService(tmp_path / "backups", today=lambda: backup_day)
    migrations.migrate_database(database_path, backup_provider=service)
    weekly_path = service.backup_dir / f"weekly-{backup_day:%G-W%V}.db"
    weekly_path.parent.mkdir(parents=True, exist_ok=True)
    weekly_path.write_text("existing weekly checkpoint", encoding="utf-8")

    created = service.backup_after_successful_learning_write(database_path)

    assert created is not None
    assert weekly_path.read_text(encoding="utf-8") == "existing weekly checkpoint"
