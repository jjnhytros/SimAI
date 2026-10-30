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


@relationships_app.command("family")
def family(character: str = typer.Option(..., "--character", "-c")) -> None:
    """Mostra genitori, figli e fratelli di un personaggio."""
    from simai.relationships.family_tree import (
        children_of,
        parents_of,
        siblings_of,
    )

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        parents = [c.key for c in parents_of(session, char.id)]
        children = [c.key for c in children_of(session, char.id)]
        siblings = [c.key for c in siblings_of(session, char.id)]
    typer.echo(f"Famiglia di '{character}':")
    typer.echo(f"  genitori: {', '.join(parents) or '—'}")
    typer.echo(f"  figli:    {', '.join(children) or '—'}")
    typer.echo(f"  fratelli: {', '.join(siblings) or '—'}")


@relationships_app.command("ancestors")
def ancestors(character: str = typer.Option(..., "--character", "-c")) -> None:
    """Mostra tutti gli antenati (BFS su PARENT_OF)."""
    from simai.relationships.family_tree import ancestors_of

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        result = [c.key for c in ancestors_of(session, char.id)]
    typer.echo(f"Antenati di '{character}': {', '.join(result) or '—'}")


@relationships_app.command("descendants")
def descendants(character: str = typer.Option(..., "--character", "-c")) -> None:
    """Mostra tutti i discendenti (BFS su PARENT_OF)."""
    from simai.relationships.family_tree import descendants_of

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        result = [c.key for c in descendants_of(session, char.id)]
    typer.echo(f"Discendenti di '{character}': {', '.join(result) or '—'}")


@relationships_app.command("kinship")
def kinship(
    character: str = typer.Option(..., "--character", "-c"),
    with_: str = typer.Option(..., "--with", "-w"),
) -> None:
    """Mostra r, r/2 e nome della relazione tra due personaggi."""
    from simai.relationships.kinship import (
        kinship_coefficient,
        relationship_coefficient,
        relationship_name,
    )

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        a = resolve_character(session, character)
        b = resolve_character(session, with_)
        r = relationship_coefficient(session, a.id, b.id)
        k = kinship_coefficient(session, a.id, b.id)
        name = relationship_name(session, a.id, b.id)
    typer.echo(f"{character} è {name} di {with_}")
    typer.echo(f"  r:    {r}")
    typer.echo(f"  r/2:  {k}")


@relationships_app.command("intimacy")
def intimacy_command(
    character: str = typer.Option(..., "--character", "-c"),
) -> None:
    """Mostra i livelli di intimità delle relazioni di un personaggio."""
    from simai.npc.intimacy.service import best_intimacy_level, intimacy_level

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        char_id = char.id
        rels = relationships_of(session, char_id)
        rows: list[tuple[str, str, float, int]] = []
        for rel in rels:
            target = session.get(Character, rel.to_character_id)
            target_key = target.key if target is not None else f"id={rel.to_character_id}"
            strength = float(rel.strength)
            rows.append((target_key, rel.kind.value, strength, intimacy_level(strength)))
        best = best_intimacy_level(session, char_id)

    if not rows:
        typer.echo(f"Intimità di '{character}': nessuna relazione")
        return
    typer.echo(f"Intimità di '{character}' (best: {best}):")
    for target_key, kind, strength, level in rows:
        typer.echo(f"  {target_key:<12} {kind:<14} strength {strength:5.1f}  livello {level}")
