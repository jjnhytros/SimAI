import typer
from sqlalchemy import select

from simai.db.session import get_engine, get_session_factory
from simai.world.models import Character, Location
from simai.world.seed import seed_muse_core

world_app = typer.Typer(help="Comandi sul mondo.")


@world_app.command("seed")
def seed() -> None:
    """Popola il Quartiere delle Muse (idempotente)."""
    engine = get_engine()
    factory = get_session_factory(engine)
    with factory() as session:
        report = seed_muse_core(session)
        session.commit()
    typer.echo(
        f"Seed Muse Core: {report['locations_created']} location, "
        f"{report['characters_created']} personaggi, "
        f"{report['needs_created']} bisogni, "
        f"{report['relationships_created']} relazioni creati."
    )


@world_app.command("list")
def list_world() -> None:
    """Mostra location e personaggi correnti."""
    engine = get_engine()
    factory = get_session_factory(engine)
    with factory() as session:
        locations = session.scalars(select(Location).order_by(Location.id)).all()
        characters = session.scalars(select(Character).order_by(Character.id)).all()

    typer.echo(f"Location ({len(locations)}):")
    for loc in locations:
        typer.echo(f"  [{loc.key}] {loc.name} — {loc.kind}")

    typer.echo(f"Personaggi ({len(characters)}):")
    for c in characters:
        marker = "★" if c.is_player else " "
        typer.echo(f"  {marker} [{c.key}] {c.name} ({c.age_years} anni)")
