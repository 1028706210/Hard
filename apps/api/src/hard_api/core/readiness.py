from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3

from alembic.script import ScriptDirectory

from hard_api.db import migrations


def database_checks(database_path: Path) -> dict[str, dict[str, object]]:
    checks = {
        "database": {"healthy": _sqlite_available(database_path), "path": str(database_path)},
        "migrations": {"healthy": _migrations_current(database_path)},
        "fts": {"healthy": _fts_available(database_path)},
    }
    return checks


def _sqlite_available(database_path: Path) -> bool:
    try:
        with closing(sqlite3.connect(f"file:{database_path.as_posix()}?mode=rw", uri=True)) as connection:
            connection.execute("SELECT 1").fetchone()
    except sqlite3.Error:
        return False
    return True


def _migrations_current(database_path: Path) -> bool:
    try:
        configuration = migrations.alembic_config(database_path)
        current = migrations.current_revision(configuration)
        return current == ScriptDirectory.from_config(configuration).get_current_head()
    except Exception:
        return False


def _fts_available(database_path: Path) -> bool:
    try:
        with closing(sqlite3.connect(f"file:{database_path.as_posix()}?mode=rw", uri=True)) as connection:
            connection.execute(
                "SELECT rowid FROM search_documents WHERE search_documents MATCH 'hard_api_readiness_probe' LIMIT 1"
            ).fetchone()
    except sqlite3.Error:
        return False
    return True
