from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from simai.config.settings import Settings


def ensure_sqlite_parent_dir(url: str) -> None:
    """Crea la directory che ospiterà il file SQLite, se manca.

    SQLite crea il file ma non la directory. Per URL non SQLite o per
    `:memory:` la funzione è no-op.
    """
    parsed = make_url(url)
    if parsed.get_backend_name() != "sqlite":
        return

    database = parsed.database
    if not database or database == ":memory:":
        return

    Path(database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def get_engine(url: str | None = None) -> Engine:
    """Crea un engine SQLAlchemy con PRAGMA sensati per SQLite."""
    settings = Settings()
    db_url = url or settings.db_url

    ensure_sqlite_parent_dir(db_url)

    engine = create_engine(db_url, future=True)

    if db_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _enable_sqlite_pragmas(dbapi_connection, _record) -> None:  # type: ignore[no-untyped-def]
            cur = dbapi_connection.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA journal_mode=WAL")
            cur.close()

    return engine


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
