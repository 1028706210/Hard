from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import shutil
import sqlite3
from contextlib import closing
from uuid import uuid4

from alembic.script import ScriptDirectory

from hard_api.backup.archive import ArchiveContents, ArchiveError, create_archive, inspect_archive
from hard_api.backup.retention import retain_backups
from hard_api.db import migrations


@dataclass(frozen=True, slots=True)
class ImportResult:
    content_version: str


class LocalBackupService:
    """SQLite backup, export and recovery operations rooted in one local directory."""

    def __init__(self, backup_dir: Path, *, today: Callable[[], date] = date.today) -> None:
        self.backup_dir = backup_dir
        self._today = today

    @staticmethod
    def _checkpoint(database_path: Path) -> None:
        with closing(sqlite3.connect(database_path)) as connection:
            connection.execute("PRAGMA wal_checkpoint(FULL)")

    @staticmethod
    def _copy_database(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(source)) as read_connection, closing(sqlite3.connect(destination)) as write_connection:
            read_connection.backup(write_connection)

    @staticmethod
    def _remove_sidecars(database_path: Path) -> None:
        for suffix in ("-wal", "-shm"):
            database_path.with_name(f"{database_path.name}{suffix}").unlink(missing_ok=True)

    def _snapshot(self, database_path: Path, prefix: str) -> Path:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint(database_path)
        snapshot = self.backup_dir / f"{prefix}-{self._today().isoformat()}-{uuid4().hex}.db"
        self._copy_database(database_path, snapshot)
        return snapshot

    def create_snapshot(self, database_path: Path) -> Path:
        return self._snapshot(database_path, "migration")

    def restore_snapshot(self, snapshot_path: Path, database_path: Path) -> None:
        if not snapshot_path.is_file():
            raise RuntimeError("恢复快照不存在。")
        candidate = database_path.with_name(f".{database_path.name}.{uuid4().hex}.restore")
        try:
            self._copy_database(snapshot_path, candidate)
            self._install_restored_database(candidate, database_path)
        finally:
            candidate.unlink(missing_ok=True)

    def _install_restored_database(self, candidate: Path, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._remove_sidecars(database_path)
        os.replace(candidate, database_path)

    def backup_after_successful_learning_write(self, database_path: Path) -> Path | None:
        daily_path = self.backup_dir / f"daily-{self._today().isoformat()}.db"
        if daily_path.exists():
            return None
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoint(database_path)
        candidate = daily_path.with_name(f".{daily_path.name}.{uuid4().hex}.tmp")
        try:
            self._copy_database(database_path, candidate)
            os.replace(candidate, daily_path)
        finally:
            candidate.unlink(missing_ok=True)
        weekly_path = self.backup_dir / f"weekly-{self._today():%G-W%V}.db"
        if not weekly_path.exists():
            self._copy_database(daily_path, weekly_path)
        retain_backups(self.backup_dir)
        return daily_path

    def export_archive(
        self,
        database_path: Path,
        destination: Path,
        *,
        settings_manifest: Mapping[str, object],
        content_version: str,
    ) -> Path:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        candidate = self.backup_dir / f"export-copy-{uuid4().hex}.db"
        try:
            self._checkpoint(database_path)
            self._copy_database(database_path, candidate)
            return create_archive(
                candidate,
                destination,
                settings_manifest=settings_manifest,
                content_version=content_version,
            )
        finally:
            candidate.unlink(missing_ok=True)

    def _validate_candidate_database(self, candidate: Path) -> None:
        with closing(sqlite3.connect(candidate)) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                raise ArchiveError("导入数据库完整性校验失败。")
        configuration = migrations.alembic_config(candidate)
        expected = ScriptDirectory.from_config(configuration).get_current_head()
        if migrations.current_revision(configuration) != expected:
            raise ArchiveError("导入数据库版本不兼容。")

    def _replace_database(self, candidate: Path, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._remove_sidecars(database_path)
        os.replace(candidate, database_path)

    def import_archive(self, archive_path: Path, database_path: Path) -> ImportResult:
        snapshot = self._snapshot(database_path, "import")
        work_directory = self.backup_dir / f"import-work-{uuid4().hex}"
        candidate = work_directory / "database.sqlite"
        try:
            contents: ArchiveContents = inspect_archive(archive_path)
            work_directory.mkdir(parents=True, exist_ok=True)
            candidate.write_bytes(contents.database_bytes)
            self._validate_candidate_database(candidate)
            self._replace_database(candidate, database_path)
            return ImportResult(content_version=contents.content_version)
        except BaseException:
            self.restore_snapshot(snapshot, database_path)
            raise
        finally:
            shutil.rmtree(work_directory, ignore_errors=True)
