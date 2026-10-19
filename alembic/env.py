import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from simai.config.settings import Settings
from simai.db.base import Base
from simai.db.registry import ensure_all_models_loaded
from simai.db.session import ensure_sqlite_parent_dir

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

ensure_all_models_loaded()
target_metadata = Base.metadata


def _resolve_url() -> str:
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        url = os.environ.get("SIMAI_DB_URL") or Settings().db_url
    ensure_sqlite_parent_dir(url)
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_resolve_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {}) or {}
    section["sqlalchemy.url"] = _resolve_url()
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()