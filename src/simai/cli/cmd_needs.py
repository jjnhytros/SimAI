import typer

from simai.cli._helpers import require_schema, resolve_character
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.needs.service import apply_decay, needs_of

needs_app = typer.Typer(help="Comandi sui bisogni.")


@needs_app.command("show")
def show(character: str = typer.Option(..., "--character", "-c")) -> None:
    """Mostra i bisogni di un personaggio."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        values = needs_of(session, char.id)
    typer.echo(f"Bisogni di '{character}':")
    for kind in NeedKind:
        v = values.get(kind)
        if v is None:
            typer.echo(f"  {kind}: (mancante)")
        else:
            typer.echo(f"  {kind}: {v:.1f}")


@needs_app.command("decay")
def decay(
    character: str = typer.Option(..., "--character", "-c"),
    minutes: int = typer.Option(..., "--minutes", "-m"),
) -> None:
    """Applica il decadimento dei bisogni per N minuti."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        result = apply_decay(session, char.id, minutes)
        session.commit()
    typer.echo(f"Bisogni dopo {minutes} minuti:")
    for kind in NeedKind:
        v = result.get(kind)
        if v is not None:
            typer.echo(f"  {kind}: {v:.1f}")
