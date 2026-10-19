import typer

from simai.actions.catalog import actions_for_location
from simai.actions.utility import choose_action, rng_for_decision
from simai.cli._helpers import require_schema, resolve_character
from simai.config.settings import Settings
from simai.db.session import get_engine, get_session_factory
from simai.needs.service import needs_of
from simai.world.models import Location

actions_app = typer.Typer(help="Comandi sulle azioni.")


@actions_app.command("choose")
def choose(
    character: str = typer.Option(..., "--character", "-c"),
    seed: int | None = typer.Option(None, "--seed"),
) -> None:
    """Scegli l'azione migliore per un personaggio (utility AI)."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    with factory() as session:
        char = resolve_character(session, character)
        loc = session.get(Location, char.location_id)
        if loc is None:
            typer.echo(
                f"Location non valida per '{character}': id={char.location_id}",
                err=True,
            )
            raise typer.Exit(code=1)
        char_id = char.id
        char_key = char.key
        char_name = char.name
        loc_name = loc.name
        loc_kind = loc.kind
        needs = needs_of(session, char_id)

    available = actions_for_location(loc_kind)
    used_seed = seed if seed is not None else Settings().master_seed
    rng = rng_for_decision(used_seed, char_id)
    choice = choose_action(needs, available, rng)

    if choice is None:
        typer.echo(
            f"Nessuna azione disponibile per '{character}' in {loc_name}.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"Personaggio: {char_name} ({char_key})")
    typer.echo(f"Location:    {loc_name} ({loc_kind})")
    typer.echo(f"Seed:        {used_seed}")
    typer.echo(f"Azione:      {choice.kind} (soddisfa {choice.satisfies})")
