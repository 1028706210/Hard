from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from threading import Thread

import pytest
from sqlalchemy import text


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


class SqliteSnapshotBackup:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def create_snapshot(self, database_path: Path) -> Path:
        self.directory.mkdir(exist_ok=True)
        snapshot_path = self.directory / "snapshot.db"
        with closing(sqlite3.connect(database_path)) as source, closing(sqlite3.connect(snapshot_path)) as destination:
            source.backup(destination)
        return snapshot_path

    def restore_snapshot(self, snapshot_path: Path, database_path: Path) -> None:
        with closing(sqlite3.connect(snapshot_path)) as source, closing(sqlite3.connect(database_path)) as destination:
            source.backup(destination)


def _migrated_database(tmp_path: Path) -> tuple[Path, object]:
    from hard_api.db import migrations, session

    database_path = tmp_path / "hard.db"
    migrations.migrate_database(database_path, backup_provider=SqliteSnapshotBackup(tmp_path / "snapshots"))
    return database_path, session


def test_write_transaction_rolls_back_every_change_when_the_operation_raises(tmp_path: Path) -> None:
    database_path, session = _migrated_database(tmp_path)

    with pytest.raises(RuntimeError, match="abort write"):
        with session.transaction(database_path) as connection:
            connection.execute(
                text(
                    "INSERT INTO settings (key, value, updated_at) "
                    "VALUES ('theme', 'dark', CURRENT_TIMESTAMP)"
                )
            )
            raise RuntimeError("abort write")

    with session.database_connection(database_path) as connection:
        setting_count = connection.execute(text("SELECT COUNT(*) FROM settings WHERE key = 'theme'")).scalar_one()

    assert setting_count == 0


def test_database_operations_use_fresh_thread_bound_sqlite_connections(tmp_path: Path) -> None:
    database_path, session = _migrated_database(tmp_path)

    with session.database_connection(database_path) as first_connection:
        first_handle = first_connection.connection.driver_connection
        thread_errors: list[BaseException] = []

        def access_connection_from_another_thread() -> None:
            try:
                first_connection.execute(text("SELECT 1"))
            except BaseException as error:
                thread_errors.append(error)

        worker = Thread(target=access_connection_from_another_thread)
        worker.start()
        worker.join()
    with session.database_connection(database_path) as second_connection:
        second_handle = second_connection.connection.driver_connection

    assert first_handle is not second_handle
    assert any("thread" in str(error).lower() for error in thread_errors)
