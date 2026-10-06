from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import text


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


REQUIRED_TABLES = {
    "settings",
    "daily_goals",
    "lesson_progress",
    "attempts",
    "submissions",
    "mastery_snapshots",
    "review_items",
    "notes",
    "favorites",
    "achievements",
    "backup_records",
    "content_versions",
    "idempotency_keys",
}


class SqliteSnapshotBackup:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.snapshots: list[Path] = []
        self.restore_calls = 0

    def create_snapshot(self, database_path: Path) -> Path:
        self.directory.mkdir(exist_ok=True)
        snapshot_path = self.directory / f"snapshot-{len(self.snapshots)}.db"
        with closing(sqlite3.connect(database_path)) as source, closing(sqlite3.connect(snapshot_path)) as destination:
            source.backup(destination)
        self.snapshots.append(snapshot_path)
        return snapshot_path

    def restore_snapshot(self, snapshot_path: Path, database_path: Path) -> None:
        self.restore_calls += 1
        with closing(sqlite3.connect(snapshot_path)) as source, closing(sqlite3.connect(database_path)) as destination:
            source.backup(destination)


def _database_modules():
    from hard_api.db import migrations, session

    return migrations, session


def test_initial_migration_creates_required_tables_and_enables_sqlite_pragmas(tmp_path: Path) -> None:
    migrations, session = _database_modules()
    database_path = tmp_path / "temporary" / "hard.db"
    backups = SqliteSnapshotBackup(tmp_path / "snapshots")

    migrations.migrate_database(database_path, backup_provider=backups)

    with session.database_connection(database_path) as connection:
        table_names = set(
            connection.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'")).scalars()
        )
        foreign_keys = connection.execute(text("PRAGMA foreign_keys")).scalar_one()
        journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar_one()

    assert REQUIRED_TABLES <= table_names
    assert foreign_keys == 1
    assert journal_mode == "wal"
    assert len(backups.snapshots) == 1
    assert migrations.current_revision(migrations.alembic_config(database_path)) == "0002_learning_engine"


def test_fts5_index_accepts_writes_and_finds_matching_documents(tmp_path: Path) -> None:
    migrations, session = _database_modules()
    database_path = tmp_path / "hard.db"

    migrations.migrate_database(database_path, backup_provider=SqliteSnapshotBackup(tmp_path / "snapshots"))
    with session.transaction(database_path) as connection:
        connection.execute(
            text(
                "INSERT INTO search_documents (document_type, document_id, content) "
                "VALUES ('lesson', 'python-foundations-intro', 'SQLite FTS5 supports full text search')"
            )
        )
    with session.database_connection(database_path) as connection:
        matching_ids = connection.execute(
            text("SELECT document_id FROM search_documents WHERE search_documents MATCH 'SQLite'")
        ).scalars().all()

    assert matching_ids == ["python-foundations-intro"]


def test_versioned_migrations_round_trip_between_head_and_base(tmp_path: Path) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"
    backups = SqliteSnapshotBackup(tmp_path / "snapshots")

    migrations.migrate_database(database_path, backup_provider=backups, target_revision="head")
    migrations.migrate_database(database_path, backup_provider=backups, target_revision="base")

    with closing(sqlite3.connect(database_path)) as connection:
        base_tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

    assert migrations.current_revision(migrations.alembic_config(database_path)) is None
    assert "settings" not in base_tables
    assert "search_documents" not in base_tables

    migrations.migrate_database(database_path, backup_provider=backups, target_revision="head")

    with closing(sqlite3.connect(database_path)) as connection:
        restored_tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        integrity_check = connection.execute("PRAGMA integrity_check").fetchone()

    assert REQUIRED_TABLES <= restored_tables
    assert "search_documents" in restored_tables
    assert integrity_check == ("ok",)


def test_learning_engine_revision_round_trips_and_preserves_initial_data(tmp_path: Path) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"
    backups = SqliteSnapshotBackup(tmp_path / "snapshots")

    migrations.migrate_database(
        database_path, backup_provider=backups, target_revision="0001_initial"
    )
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES ('legacy', 'kept', '2026-08-24')"
            )

    migrations.migrate_database(database_path, backup_provider=backups, target_revision="head")

    assert migrations.current_revision(migrations.alembic_config(database_path)) == "0002_learning_engine"

    with closing(sqlite3.connect(database_path)) as connection:
        legacy_setting = connection.execute("SELECT value FROM settings WHERE key = 'legacy'").fetchone()
        new_tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

    assert legacy_setting == ("kept",)
    assert {"learning_activity_days", "experience_events"} <= new_tables

    migrations.migrate_database(
        database_path, backup_provider=backups, target_revision="0001_initial"
    )
    with closing(sqlite3.connect(database_path)) as connection:
        downgraded_tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    assert "learning_activity_days" not in downgraded_tables
    assert "experience_events" not in downgraded_tables

    migrations.migrate_database(database_path, backup_provider=backups, target_revision="head")
    with closing(sqlite3.connect(database_path)) as connection:
        integrity_check = connection.execute("PRAGMA integrity_check").fetchone()
        active_review_index = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' "
            "AND name = 'ux_review_items_active_lesson_exercise'"
        ).fetchone()

    assert migrations.current_revision(migrations.alembic_config(database_path)) == "0002_learning_engine"
    assert integrity_check == ("ok",)
    assert active_review_index == ("ux_review_items_active_lesson_exercise",)
    assert len(backups.snapshots) == 4


def test_upgrade_head_is_a_no_op_when_database_is_already_current(tmp_path: Path) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"
    migrations.migrate_database(
        database_path,
        backup_provider=SqliteSnapshotBackup(tmp_path / "initial-snapshots"),
        target_revision="head",
    )

    class BackupThatMustNotRun:
        def create_snapshot(self, _database_path: Path) -> Path:
            raise AssertionError("current database must not start a migration")

        def restore_snapshot(self, _snapshot_path: Path, _database_path: Path) -> None:
            raise AssertionError("current database must not restore a snapshot")

    migrations.migrate_database(
        database_path,
        backup_provider=BackupThatMustNotRun(),
        target_revision="head",
    )

    assert migrations.current_revision(migrations.alembic_config(database_path)) == "0002_learning_engine"


def test_direct_alembic_upgrade_without_an_authorized_connection_cannot_create_schema(
    tmp_path: Path,
) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"

    with pytest.raises(RuntimeError, match="migrate_database"):
        command.upgrade(migrations.alembic_config(database_path), "head")

    with closing(sqlite3.connect(database_path)) as connection:
        table_names = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

    assert "settings" not in table_names
    assert "alembic_version" not in table_names


def test_direct_alembic_downgrade_without_an_authorized_connection_preserves_head(
    tmp_path: Path,
) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"
    migrations.migrate_database(
        database_path,
        backup_provider=SqliteSnapshotBackup(tmp_path / "snapshots"),
        target_revision="head",
    )

    with pytest.raises(RuntimeError, match="migrate_database"):
        command.downgrade(migrations.alembic_config(database_path), "base")

    with closing(sqlite3.connect(database_path)) as connection:
        settings_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'settings'"
        ).fetchone()
        version = connection.execute("SELECT version_num FROM alembic_version").fetchone()

    assert settings_table == ("settings",)
    assert version == ("0002_learning_engine",)


def test_failed_alembic_upgrade_restores_after_a_committed_destructive_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("CREATE TABLE legacy_state (value TEXT NOT NULL)")
            connection.execute("INSERT INTO legacy_state (value) VALUES ('keep me')")

    def destructive_upgrade(_configuration, _target_revision: str) -> None:
        with closing(sqlite3.connect(database_path)) as connection:
            with connection:
                connection.execute("DROP TABLE legacy_state")
        raise RuntimeError("migration interrupted after destructive change")

    backups = SqliteSnapshotBackup(tmp_path / "snapshots")
    monkeypatch.setattr(migrations.command, "upgrade", destructive_upgrade)
    with pytest.raises(RuntimeError, match="migration interrupted"):
        migrations.migrate_database(
            database_path,
            backup_provider=backups,
            target_revision="head",
        )

    with closing(sqlite3.connect(database_path)) as connection:
        restored_value = connection.execute("SELECT value FROM legacy_state").fetchone()

    assert restored_value == ("keep me",)
    assert backups.restore_calls == 1


def test_backup_failure_prevents_any_migration_work(tmp_path: Path) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("CREATE TABLE legacy_state (value TEXT NOT NULL)")
            connection.execute("INSERT INTO legacy_state (value) VALUES ('keep me')")

    class FailingBackup:
        def create_snapshot(self, _database_path: Path) -> Path:
            raise OSError("backup disk unavailable")

        def restore_snapshot(self, _snapshot_path: Path, _database_path: Path) -> None:
            raise AssertionError("restore must not run when snapshot creation fails")

    with pytest.raises(OSError, match="backup disk unavailable"):
        migrations.migrate_database(
            database_path,
            backup_provider=FailingBackup(),
            target_revision="head",
        )

    with closing(sqlite3.connect(database_path)) as connection:
        legacy_value = connection.execute("SELECT value FROM legacy_state").fetchone()
        migrated_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'settings'"
        ).fetchone()

    assert legacy_value == ("keep me",)
    assert migrated_table is None


def test_missing_backup_snapshot_prevents_any_migration_work(tmp_path: Path) -> None:
    migrations, _session = _database_modules()
    database_path = tmp_path / "hard.db"

    class MissingSnapshotBackup:
        def create_snapshot(self, _database_path: Path) -> Path:
            return tmp_path / "missing.db"

        def restore_snapshot(self, _snapshot_path: Path, _database_path: Path) -> None:
            raise AssertionError("restore must not run when the snapshot is absent")

    with pytest.raises(RuntimeError, match="迁移前备份不存在"):
        migrations.migrate_database(
            database_path,
            backup_provider=MissingSnapshotBackup(),
            target_revision="head",
        )

    with closing(sqlite3.connect(database_path)) as connection:
        migrated_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'settings'"
        ).fetchone()

    assert migrated_table is None
