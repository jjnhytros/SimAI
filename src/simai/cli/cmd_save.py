from pathlib import Path

import typer

from simai.cli._helpers import require_schema
from simai.db.session import get_engine, get_session_factory
from simai.save.errors import SaveError
from simai.save.service import (
    create_save,
    delete_save,
    list_saves,
    load_save,
)

save_app = typer.Typer(help="Comandi sui salvataggi.")


@save_app.command("create")
def create(
    name: str | None = typer.Option(None, "--name", "-n"),
    output: Path | None = typer.Option(None, "--output", "-o"),
) -> None:
    """Crea un file .sav dallo stato corrente."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        try:
            info = create_save(session, name=name, output=output)
        except SaveError as exc:
            typer.echo(f"Errore: {exc}", err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(f"Salvataggio creato: {info.path}")
    typer.echo(f"  tick: {info.header.tick_index}")
    typer.echo(f"  seed: {info.header.master_seed}")
    typer.echo(f"  dimensione: {info.size_bytes} byte")


@save_app.command("list")
def list_command() -> None:
    """Elenca i salvataggi disponibili."""
    saves = list_saves()
    if not saves:
        typer.echo("Nessun salvataggio trovato.")
        return
    typer.echo(f"Salvataggi ({len(saves)}):")
    for s in saves:
        typer.echo(
            f"  {s.name:<32} tick={s.header.tick_index:<6} "
            f"seed={s.header.master_seed:<6} "
            f"{s.size_bytes:>7} B  {s.header.created_at}"
        )


@save_app.command("load")
def load(
    name: str = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Carica un salvataggio, sostituendo lo stato corrente."""
    if not yes:
        confirmed = typer.confirm(
            "Sovrascrivere lo stato corrente con il salvataggio?",
        )
        if not confirmed:
            typer.echo("Operazione annullata.")
            raise typer.Exit(code=0)

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        try:
            header = load_save(session, name)
        except SaveError as exc:
            typer.echo(f"Errore: {exc}", err=True)
            raise typer.Exit(code=1) from exc
        session.commit()
    typer.echo("Salvataggio caricato.")
    typer.echo(f"  tick: {header.tick_index}")
    typer.echo(f"  seed: {header.master_seed}")


@save_app.command("delete")
def delete(
    name: str = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Elimina un file .sav."""
    if not yes:
        confirmed = typer.confirm("Eliminare il file di salvataggio?")
        if not confirmed:
            typer.echo("Operazione annullata.")
            raise typer.Exit(code=0)
    try:
        path = delete_save(name)
    except SaveError as exc:
        typer.echo(f"Errore: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"File eliminato: {path}")


@save_app.command("inspect")
def inspect(name: str = typer.Argument(...)) -> None:
    """Mostra i metadati di un file .sav senza caricarlo."""
    from simai.save.format import decode
    from simai.save.service import _resolve_path

    try:
        path = _resolve_path(name)
    except SaveError as exc:
        typer.echo(f"Errore: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    header, _ = decode(path.read_bytes())
    typer.echo(f"File:          {path}")
    typer.echo(f"Formato:       v{header.version}")
    typer.echo(f"SimAI:         {header.simai_version}")
    typer.echo(f"Creato:        {header.created_at}")
    typer.echo(f"Schema:        {header.schema_revision}")
    typer.echo(f"Tick:          {header.tick_index}")
    typer.echo(f"Seed:          {header.master_seed}")
    typer.echo(f"Checksum:      {header.checksum}")
