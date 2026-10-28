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


@npc_app.command("kill")
def kill_command(
    character: str = typer.Option(..., "--character", "-c"),
    cause: str = typer.Option("manual", "--cause"),
) -> None:
    """Uccide un personaggio (rimuove, distribuisce balance)."""
    from simai.npc.death import kill
    from simai.sim.state import get_state
    from simai.world.enums import DeathCause

    try:
        death_cause = DeathCause(cause)
    except ValueError:
        typer.echo(
            f"Causa non valida: {cause}. Valide: {', '.join(d.value for d in DeathCause)}",
            err=True,
        )
        raise typer.Exit(code=1)

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        state = get_state(session)
        result = kill(
            session,
            character,
            cause=death_cause,
            tick_index=state.tick_index,
        )
        session.commit()
    if not result.success:
        typer.echo(f"Errore: {result.error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{result.character_key} ucciso ({result.cause.value})")
    if result.inheritance is not None:
        typer.echo(f"  erede tier: {result.inheritance.tier}")
        for k, v in result.inheritance.allocations.items():
            typer.echo(f"  → {k}: {v:.1f} Athel")
        if result.inheritance.to_world > 0:
            typer.echo(f"  → world: {result.inheritance.to_world:.1f} Athel")


@npc_app.command("lifecycle-tick")
def lifecycle_tick(
    tick: int | None = typer.Option(None, "--tick"),
) -> None:
    """Esegue `LifecycleManager.daily_tick` a un tick arbitrario."""
    from simai.npc.lifecycle import LifecycleManager
    from simai.sim.state import get_state

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        state = get_state(session)
        used_tick = tick if tick is not None else state.tick_index
        kills, deliveries = LifecycleManager().daily_tick(
            session, used_tick, master_seed=state.master_seed
        )
        session.commit()
    typer.echo(f"Lifecycle tick {used_tick}: {len(kills)} morti, {len(deliveries)} parti")
    for k in kills:
        typer.echo(f"  morto: {k.character_key} ({k.cause.value})")
    for d in deliveries:
        if d.success:
            typer.echo(f"  parto: {', '.join(d.children_keys)}")
        else:
            typer.echo(f"  parto fallito: {d.error}", err=True)


@npc_app.command("conceive")
def conceive_command(
    character: str = typer.Option(..., "--character", "-c"),
    partner: str = typer.Option(..., "--partner", "-p"),
) -> None:
    """Crea una gravidanza."""
    from simai.npc.pregnancy import conceive
    from simai.sim.state import get_state

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        state = get_state(session)
        result = conceive(
            session,
            character,
            partner,
            tick_index=state.tick_index,
            master_seed=state.master_seed,
        )
        session.commit()
    if not result.success:
        typer.echo(f"Errore: {result.error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Gravidanza creata: {result.pregnancy_id}")
    typer.echo(f"  parto previsto: tick {result.due_at_tick}")


@npc_app.command("pregnancies")
def pregnancies_command() -> None:
    """Elenca le gravidanze in corso."""
    from sqlalchemy import select as sa_select

    from simai.world.models import Character, Pregnancy

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        rows = session.scalars(sa_select(Pregnancy).order_by(Pregnancy.id)).all()
        lines: list[str] = []
        for p in rows:
            parent = session.get(Character, p.character_id)
            partner = session.get(Character, p.partner_id) if p.partner_id else None
            lines.append(
                f"  #{p.id}: {parent.key if parent else '?'} "
                f"(partner: {partner.key if partner else '—'}) "
                f"concepita {p.conceived_at_tick}, "
                f"parto {p.due_at_tick}"
            )
    typer.echo(f"Gravidanze ({len(rows)}):")
    for line in lines:
        typer.echo(line)


@npc_app.command("deliver")
def deliver_command(
    character: str = typer.Option(..., "--character", "-c"),
) -> None:
    """Forza il parto della gravidanza di un personaggio."""
    from sqlalchemy import select as sa_select

    from simai.npc.pregnancy import deliver
    from simai.sim.state import get_state
    from simai.world.models import Character, Pregnancy

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        parent = session.query(Character).filter_by(key=character).one_or_none()
        if parent is None:
            typer.echo(f"Personaggio non trovato: {character}", err=True)
            raise typer.Exit(code=1)
        pregnancy = session.scalar(sa_select(Pregnancy).where(Pregnancy.character_id == parent.id))
        if pregnancy is None:
            typer.echo(f"Nessuna gravidanza per {character}", err=True)
            raise typer.Exit(code=1)
        state = get_state(session)
        result = deliver(session, pregnancy, master_seed=state.master_seed)
        session.commit()
    if not result.success:
        typer.echo(f"Errore: {result.error}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Parto: {', '.join(result.children_keys)}")
