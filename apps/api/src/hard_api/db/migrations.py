from __future__ import annotations

from pathlib import Path
from typing import Protocol

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from hard_api.db.session import create_database_engine


API_DIRECTORY = Path(__file__).resolve().parents[3]
ALEMBIC_INI_PATH = API_DIRECTORY / "alembic.ini"
ALEMBIC_DIRECTORY = API_DIRECTORY / "alembic"
AUTHORIZED_CONNECTION_ATTRIBUTE = "hard_api_authorized_migration_connection"


class BackupProvider(Protocol):
    def create_snapshot(self, database_path: Path) -> Path: ...

    def restore_snapshot(self, snapshot_path: Path, database_path: Path) -> None: ...


def alembic_config(database_path: Path) -> Config:
    configuration = Config(str(ALEMBIC_INI_PATH))
    configuration.set_main_option("script_location", str(ALEMBIC_DIRECTORY))
    configuration.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.resolve().as_posix()}")
    return configuration


def current_revision(configuration: Config) -> str | None:
    engine = create_engine(
        configuration.get_main_option("sqlalchemy.url"),
        connect_args={"check_same_thread": True},
        poolclass=NullPool,
    )
    try:
        with engine.connect() as connection:
            return MigrationContext.configure(connection).get_current_revision()
    finally:
        engine.dispose()


def _target_revision(configuration: Config, target_revision: str) -> str | None:
    script_directory = ScriptDirectory.from_config(configuration)
    if target_revision == "head":
        return script_directory.get_current_head()
    if target_revision == "base":
        return None
    return script_directory.as_revision_number(target_revision)


def _requires_downgrade(
    configuration: Config, current: str | None, target: str | None
) -> bool:
    if target is None:
        return current is not None
    if current is None:
        return False
    script_directory = ScriptDirectory.from_config(configuration)
    current_lineage = {
        revision.revision for revision in script_directory.iterate_revisions(current, "base")
    }
    return target in current_lineage


def migrate_database(
    database_path: Path,
    *,
    backup_provider: BackupProvider,
    target_revision: str = "head",
) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if not database_path.exists():
        database_path.touch()

    configuration = alembic_config(database_path)
    current = current_revision(configuration)
    target = _target_revision(configuration, target_revision)
    if current == target:
        return

    snapshot_path = backup_provider.create_snapshot(database_path)
    if not snapshot_path.exists():
        raise RuntimeError(f"迁移前备份不存在：{snapshot_path}")

    try:
        migration_engine = create_database_engine(database_path)
        try:
            with migration_engine.connect() as connection:
                configuration.attributes[AUTHORIZED_CONNECTION_ATTRIBUTE] = connection
                if _requires_downgrade(configuration, current, target):
                    command.downgrade(configuration, target_revision)
                else:
                    command.upgrade(configuration, target_revision)
        finally:
            configuration.attributes.pop(AUTHORIZED_CONNECTION_ATTRIBUTE, None)
            migration_engine.dispose()
    except BaseException:
        backup_provider.restore_snapshot(snapshot_path, database_path)
        raise
