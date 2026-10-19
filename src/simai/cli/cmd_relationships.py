import typer

from simai.cli._helpers import require_schema, resolve_character
from simai.db.session import get_engine, get_session_factory
from simai.relationships.service import relationships_of
from simai.world.models import Character

relationships_app = typer.Typer(help="Comandi sulle relazioni.")


@relationships_app.command("show")
def show(
    character: str = typer.Option(..., "--character", "-c"),
) -> None:
    """Mostra le relazioni in uscita di un personaggio."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        rels = relationships_of(session, char.id)
        lines: list[str] = []
        for rel in rels:
            target = session.get(Character, rel.to_character_id)
            target_label = target.key if target is not None else f"id={rel.to_character_id}"
            lines.append(f"  → [{target_label}] {rel.kind.value.upper()} {rel.strength:.1f}")
    typer.echo(f"Relazioni di '{character}' ({len(rels)}):")
    for line in lines:
        typer.echo(line)
