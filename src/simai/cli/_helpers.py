import typer
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from simai.db.alembic_utils import get_alembic_config
from simai.world.models import Character


def require_schema(engine: Engine) -> None:
    """Interrompe con messaggio comprensibile se lo schema non è pronto."""
    cfg = get_alembic_config()
    head = ScriptDirectory.from_config(cfg).get_current_head()

    with engine.connect() as conn:
        current = MigrationContext.configure(conn).get_current_revision()

    if current is None:
        typer.echo(
            "Database non inizializzato. Esegui `simai db upgrade`.",
            err=True,
        )
        raise typer.Exit(code=1)

    if head is not None and current != head:
        typer.echo(
            f"Schema DB non aggiornato (corrente={current}, "
            f"attesa={head}). Esegui `simai db upgrade`.",
            err=True,
        )
        raise typer.Exit(code=1)


def resolve_character(session: Session, key: str) -> Character:
    char = session.scalar(select(Character).where(Character.key == key))
    if char is None:
        typer.echo(f"Personaggio non trovato: {key}", err=True)
        raise typer.Exit(code=1)
    return char
