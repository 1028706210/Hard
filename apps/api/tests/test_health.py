from collections.abc import Iterator
from contextlib import closing
import json
import sqlite3
import sys
from tempfile import TemporaryDirectory
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hard_api.core.config import Settings
from hard_api.backup.service import LocalBackupService
from hard_api.db import migrations
from hard_api.main import create_app


@pytest.fixture()
def d_temp_path() -> Iterator[Path]:
    cache_dir = Path(__file__).resolve().parents[3] / ".tool-cache"
    cache_dir.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=cache_dir) as temporary_directory:
        yield Path(temporary_directory)


def test_live_health_and_request_id_are_available() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_ready_reports_each_dependency_and_a_missing_runner(d_temp_path: Path) -> None:
    lock_path = d_temp_path / "toolchain-lock.json"
    lock_path.write_text(
        json.dumps(
            [
                {"name": "python", "healthy": True, "path": "D:/DevTools/python/python.exe"},
                {"name": "java", "healthy": True, "path": "D:/Java/bin/javac.exe"},
                {"name": "dotnet", "healthy": False, "path": "D:/DevTools/dotnet/dotnet.exe"},
                {"name": "msys2-gcc", "healthy": True, "path": "D:/DevTools/msys64/ucrt64/bin/g++.exe"},
            ]
        ),
        encoding="utf-8",
    )
    settings = Settings.from_environment(
        project_root=d_temp_path,
        environment={"HARD_TOOLCHAIN_LOCK": lock_path.name},
    )
    settings.content_dir.mkdir()
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))

    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health/ready")

    checks = response.json()["checks"]
    assert response.status_code == 503
    assert set(checks) == {"database", "migrations", "fts", "content", "python", "java", "csharp", "cpp"}
    assert checks["csharp"]["healthy"] is False
    assert checks["csharp"]["path"] == "D:/DevTools/dotnet/dotnet.exe"


def test_ready_reads_a_utf8_bom_toolchain_lock(d_temp_path: Path) -> None:
    lock_path = d_temp_path / "toolchain-lock.json"
    lock_path.write_bytes(
        b"\xef\xbb\xbf"
        + json.dumps(
            [
                {"name": "python", "healthy": True, "path": "D:/DevTools/python/python.exe"},
                {"name": "java", "healthy": True, "path": "D:/Java/bin/javac.exe"},
                {"name": "dotnet", "healthy": True, "path": "D:/DevTools/dotnet/dotnet.exe"},
                {"name": "msys2-gcc", "healthy": True, "path": "D:/DevTools/msys64/ucrt64/bin/g++.exe"},
            ]
        ).encode("utf-8")
    )
    settings = Settings.from_environment(
        project_root=d_temp_path,
        environment={"HARD_TOOLCHAIN_LOCK": lock_path.name},
    )
    settings.content_dir.mkdir()
    migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))

    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json()["checks"]["python"]["healthy"] is True
    assert response.json()["checks"]["java"]["healthy"] is True
    assert response.json()["checks"]["csharp"]["healthy"] is True
    assert response.json()["checks"]["cpp"]["healthy"] is True


@pytest.mark.parametrize("failure", ["sqlite", "migration", "fts"])
def test_ready_fails_closed_when_sqlite_migrations_or_fts_are_unavailable(
    d_temp_path: Path, failure: str
) -> None:
    settings = Settings.from_environment(project_root=d_temp_path, environment={})
    settings.content_dir.mkdir()
    if failure == "sqlite":
        settings.database_path.mkdir(parents=True)
    else:
        migrations.migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
        if failure == "migration":
            with closing(sqlite3.connect(settings.database_path)) as connection:
                with connection:
                    connection.execute("DELETE FROM alembic_version")
        else:
            with closing(sqlite3.connect(settings.database_path)) as connection:
                with connection:
                    connection.execute("DROP TABLE search_documents")

    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    check_name = {"sqlite": "database", "migration": "migrations", "fts": "fts"}[failure]
    assert response.json()["checks"][check_name]["healthy"] is False


def test_settings_rejects_c_drive_data_directory() -> None:
    try:
        Settings.from_environment(
            project_root=Path("D:/Hard-test"),
            environment={"HARD_DATA_DIR": "C:/unsafe-data"},
        )
    except ValueError as error:
        assert "C" in str(error)
    else:
        raise AssertionError("C drive data directory must be rejected")


def test_settings_rejects_c_drive_relative_data_directory() -> None:
    try:
        Settings.from_environment(
            project_root=Path("D:/Hard-test"),
            environment={"HARD_DATA_DIR": "C:unsafe-data"},
        )
    except ValueError as error:
        assert "C" in str(error)
    else:
        raise AssertionError("C drive-relative data directory must be rejected")


def test_settings_rejects_c_drive_project_root() -> None:
    try:
        Settings.from_environment(
            project_root=Path("C:/Hard"),
            environment={},
        )
    except ValueError as error:
        assert "D" in str(error)
    else:
        raise AssertionError("project root outside D drive must be rejected")


def test_settings_rejects_paths_outside_the_project_root() -> None:
    try:
        Settings.from_environment(
            project_root=Path("D:/Hard-test"),
            environment={"HARD_DATA_DIR": "../outside"},
        )
    except ValueError as error:
        assert "项目根目录" in str(error)
    else:
        raise AssertionError("data directory outside the project root must be rejected")
