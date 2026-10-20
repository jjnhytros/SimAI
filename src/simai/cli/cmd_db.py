import typer
from alembic import command
from alembic.runtime.migration import MigrationContext

from simai.config.settings import Settings
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine

db_app = typer.Typer(help="Comandi sul database.")


@db_app.command("upgrade")
def upgrade(revision: str = "head") -> None:
    """Applica le migrazioni fino alla revisione indicata (default: head)."""
    cfg = get_alembic_config()
    command.upgrade(cfg, revision)
    typer.echo(f"DB aggiornato a: {revision}")


@db_app.command("downgrade")
def downgrade(revision: str = "-1") -> None:
    """Riporta indietro le migrazioni."""
    cfg = get_alembic_config()
    command.downgrade(cfg, revision)
    typer.echo(f"DB riportato a: {revision}")


@db_app.command("status")
def status() -> None:
    """Mostra la revisione Alembic corrente."""
    settings = Settings()
    engine = get_engine(settings.db_url)
    with engine.connect() as conn:
        current = MigrationContext.configure(conn).get_current_revision()

    if current is None:
        typer.echo("DB non inizializzato.")
        raise typer.Exit(code=1)

    typer.echo(f"Revisione corrente: {current}")
