from __future__ import annotations

from alembic import context

from hard_api.db.base import Base
import hard_api.db.models  # noqa: F401


config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    raise RuntimeError(
        "数据库迁移必须通过 migrate_database() 执行，且只能使用已授权的注入连接"
    )


def run_migrations_online() -> None:
    connection = config.attributes.get("hard_api_authorized_migration_connection")
    if connection is None:
        raise RuntimeError(
            "数据库迁移必须通过 migrate_database() 执行，且只能使用已授权的注入连接"
        )

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        transaction_per_migration=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
