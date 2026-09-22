"""Alembic environment — legge SIMAI_DB_URL dalle settings SimAI."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from simai.config.settings import get_settings
from simai.db.base import Base
from simai.db.registry import ensure_all_models_loaded

# Carica tutti i modelli (side-effect) — garantisce che Base.metadata contenga
# tutte le tabelle, indipendentemente da quali package siano importati altrove.
ensure_all_models_loaded()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

_settings = get_settings()
config.set_main_option("sqlalchemy.url", _settings.db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Esegue le migrazioni in modalità 'offline' (solo SQL generato)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Esegue le migrazioni in modalità 'online' (connessione attiva)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
