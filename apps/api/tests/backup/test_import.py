from __future__ import annotations

import json
import sqlite3
import sys
import zipfile
from contextlib import closing
from datetime import date
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from hard_api.backup.archive import ArchiveError, inspect_archive
import hard_api.backup.service as backup_service
from hard_api.backup.service import LocalBackupService
from hard_api.db import migrations


def migrated_database(tmp_path: Path) -> tuple[Path, LocalBackupService]:
    database_path = tmp_path / "data" / "hard.db"
    service = LocalBackupService(tmp_path / "backups", today=lambda: date(2026, 8, 25))
    migrations.migrate_database(database_path, backup_provider=service)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES ('restore-me', 'before-export', CURRENT_TIMESTAMP)"
            )
    return database_path, service


def test_export_has_only_allowlisted_entries_with_sha256_and_import_restores_database(tmp_path: Path) -> None:
    database_path, service = migrated_database(tmp_path)
    archive_path = service.export_archive(
        database_path,
        tmp_path / "exports" / "hard-export.zip",
        settings_manifest={"format_version": 1},
        content_version="sha256-content-version",
    )
    with zipfile.ZipFile(archive_path) as archive:
        assert set(archive.namelist()) == {"database.sqlite", "settings.json", "content-version.json", "manifest.json"}
        manifest = json.loads(archive.read("manifest.json"))
    assert manifest["format_version"] == 1
    assert {record["path"] for record in manifest["files"]} == {"database.sqlite", "settings.json", "content-version.json"}

    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("UPDATE settings SET value = 'after-export' WHERE key = 'restore-me'")
    result = service.import_archive(archive_path, database_path)

    assert result.content_version == "sha256-content-version"
    with closing(sqlite3.connect(database_path)) as connection:
        assert connection.execute("SELECT value FROM settings WHERE key = 'restore-me'").fetchone() == ("before-export",)
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)


def test_inspection_rejects_path_traversal_duplicate_entries_and_checksum_mismatch(tmp_path: Path) -> None:
    database_path, service = migrated_database(tmp_path)
    archive_path = service.export_archive(
        database_path, tmp_path / "exports" / "source.zip", settings_manifest={}, content_version="v1"
    )
    duplicate = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(duplicate, "w") as archive:
        archive.writestr("database.sqlite", "one")
        archive.writestr("database.sqlite", "two")
    with pytest.raises(ArchiveError, match="重复"):
        inspect_archive(duplicate)

    traversal = tmp_path / "traversal.zip"
    with zipfile.ZipFile(traversal, "w") as archive:
        archive.writestr("../database.sqlite", "unsafe")
    with pytest.raises(ArchiveError, match="路径"):
        inspect_archive(traversal)

    absolute = tmp_path / "absolute.zip"
    with zipfile.ZipFile(absolute, "w") as archive:
        archive.writestr("/database.sqlite", "unsafe")
    with pytest.raises(ArchiveError, match="路径"):
        inspect_archive(absolute)

    corrupt = tmp_path / "corrupt.zip"
    with zipfile.ZipFile(archive_path) as source, zipfile.ZipFile(corrupt, "w") as target:
        for info in source.infolist():
            target.writestr(info.filename, b"changed" if info.filename == "database.sqlite" else source.read(info.filename))
    with pytest.raises(ArchiveError, match="校验"):
        inspect_archive(corrupt)

    incompatible = tmp_path / "incompatible.zip"
    with zipfile.ZipFile(archive_path) as source, zipfile.ZipFile(incompatible, "w") as target:
        for info in source.infolist():
            target.writestr(
                info.filename,
                json.dumps({"format_version": 2, "files": []}).encode("utf-8")
                if info.filename == "manifest.json"
                else source.read(info.filename),
            )
    with pytest.raises(ArchiveError, match="版本"):
        inspect_archive(incompatible)


def test_incompatible_or_failed_import_restores_the_preimport_database(tmp_path: Path, monkeypatch) -> None:
    database_path, service = migrated_database(tmp_path)
    archive_path = service.export_archive(
        database_path, tmp_path / "exports" / "source.zip", settings_manifest={}, content_version="v1"
    )
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("UPDATE settings SET value = 'current' WHERE key = 'restore-me'")

    def destructive_replace(_candidate: Path, target: Path) -> None:
        with closing(sqlite3.connect(target)) as connection:
            with connection:
                connection.execute("DELETE FROM settings WHERE key = 'restore-me'")
        raise RuntimeError("replacement interrupted")

    monkeypatch.setattr(service, "_replace_database", destructive_replace)
    with pytest.raises(RuntimeError, match="replacement interrupted"):
        service.import_archive(archive_path, database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        assert connection.execute("SELECT value FROM settings WHERE key = 'restore-me'").fetchone() == ("current",)
    assert list((tmp_path / "backups").glob("import-*.db"))


def test_import_validation_rejects_a_database_at_an_outdated_schema_revision(tmp_path: Path) -> None:
    _database_path, service = migrated_database(tmp_path)
    candidate = tmp_path / "candidate.db"
    with closing(sqlite3.connect(candidate)):
        pass

    with pytest.raises(ArchiveError, match="版本不兼容"):
        service._validate_candidate_database(candidate)


def test_import_validation_translates_a_failed_integrity_check_to_an_archive_error(tmp_path: Path, monkeypatch) -> None:
    class IntegrityCheck:
        def fetchone(self) -> tuple[str]:
            return ("corrupt",)

    class CorruptConnection:
        def execute(self, _statement: str) -> IntegrityCheck:
            return IntegrityCheck()

        def close(self) -> None:
            pass

    service = LocalBackupService(tmp_path / "backups")
    monkeypatch.setattr(backup_service.sqlite3, "connect", lambda _candidate: CorruptConnection())

    with pytest.raises(ArchiveError, match="完整性"):
        service._validate_candidate_database(tmp_path / "corrupt.db")
