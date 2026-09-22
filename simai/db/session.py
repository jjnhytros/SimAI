"""Engine SQLAlchemy, session factory e context manager."""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from simai.config.settings import get_settings


def sqlite_path_from_url(url: str) -> Path | None:
    """Estrae il path filesystem da una URL SQLite. ``None`` se non è file-based."""
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return None
    raw = url.removeprefix(prefix)
    if raw == ":memory:" or raw.startswith("file::memory:"):
        return None
    return Path(raw)


def _build_engine() -> Engine:
    """Costruisce l'engine a partire dalle settings correnti."""
    # Side-effect: garantisce che tutte le tabelle siano in Base.metadata
    # prima di creare l'engine. Necessario per FK cross-package
    # (es. character.location_id -> location.id).
    from simai.db.registry import ensure_all_models_loaded

    ensure_all_models_loaded()

    settings = get_settings()
    url = settings.db_url

    connect_args: dict[str, object] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(url, connect_args=connect_args, future=True)

    if url.startswith("sqlite"):
        _register_sqlite_pragmas(engine)

    return engine


def _register_sqlite_pragmas(engine: Engine) -> None:
    """Registra i PRAGMA SQLite all'apertura di ogni connessione."""

    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_connection: Any, _connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Restituisce l'engine singleton."""
    return _build_engine()


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Restituisce la session factory singleton."""
    return sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        future=True,
    )


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager che gestisce commit/rollback/chiusura automaticamente."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
