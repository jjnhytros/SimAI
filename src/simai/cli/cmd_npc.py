import typer

from simai.cli._helpers import require_schema, resolve_character
from simai.db.session import get_engine, get_session_factory
from simai.npc.traits import (
    TRAIT_DECAY_MODIFIERS,
    TRAIT_UTILITY_BONUS,
    Trait,
)

npc_app = typer.Typer(help="Comandi sugli NPC.")


def _trait_summary(trait: Trait) -> str:
    decay = TRAIT_DECAY_MODIFIERS.get(trait, {})
    util = TRAIT_UTILITY_BONUS.get(trait, {})
    parts: list[str] = []
    for kind, mult in decay.items():
        delta = (mult - 1.0) * 100
        parts.append(f"{kind.value} {delta:+.0f}%")
    for action, bonus in util.items():
        parts.append(f"{action.value} +{bonus:.2f}")
    return ", ".join(parts) if parts else "nessun effetto"


@npc_app.command("traits")
def traits(
    character: str = typer.Option(..., "--character", "-c"),
) -> None:
    """Mostra i tratti di un personaggio e i loro effetti."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        char = resolve_character(session, character)
        char_traits = list(char.traits)

    if not char_traits:
        typer.echo(f"Tratti di '{character}': nessuno")
        return

    typer.echo(f"Tratti di '{character}' ({len(char_traits)}):")
    for raw in char_traits:
        try:
            t = Trait(raw)
        except ValueError:
            typer.echo(f"  {raw}: (sconosciuto)")
            continue
        typer.echo(f"  {t.value:<10} {_trait_summary(t)}")
