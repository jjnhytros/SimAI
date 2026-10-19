import typer
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.needs.service import apply_decay, needs_of
from simai.world.models import Character

needs_app = typer.Typer(help="Comandi sui bisogni.")


def _character_id(session: Session, key: str) -> int:
    char = session.scalar(select(Character).where(Character.key == key))
    if char is None:
        typer.echo(f"Personaggio non trovato: {key}", err=True)
        raise typer.Exit(code=1)
    return char.id


@needs_app.command("show")
def show(character: str = typer.Option(..., "--character", "-c")) -> None:
    """Mostra i bisogni di un personaggio."""
    engine = get_engine()
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _character_id(session, character)
        values = needs_of(session, cid)
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
    factory = get_session_factory(engine)
    with factory() as session:
        cid = _character_id(session, character)
        result = apply_decay(session, cid, minutes)
        session.commit()
    typer.echo(f"Bisogni dopo {minutes} minuti:")
    for kind in NeedKind:
        v = result.get(kind)
        if v is not None:
            typer.echo(f"  {kind}: {v:.1f}")
