from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.pool import NullPool


def create_database_engine(database_path: Path) -> Engine:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{database_path.resolve().as_posix()}",
        connect_args={"check_same_thread": True},
        poolclass=NullPool,
    )

    @event.listens_for(engine, "connect")
    def configure_sqlite_connection(dbapi_connection, _connection_record) -> None:
        dbapi_connection.execute("PRAGMA foreign_keys = ON")
        dbapi_connection.execute("PRAGMA journal_mode = WAL")

    return engine


@contextmanager
def database_connection(database_path: Path) -> Iterator[Connection]:
    engine = create_database_engine(database_path)
    try:
        with engine.connect() as connection:
            yield connection
    finally:
        engine.dispose()


@contextmanager
def transaction(database_path: Path) -> Iterator[Connection]:
    engine = create_database_engine(database_path)
    try:
        with engine.begin() as connection:
            yield connection
    finally:
        engine.dispose()
