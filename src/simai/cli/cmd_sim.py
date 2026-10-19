import typer

from simai.cli._helpers import require_schema
from simai.config.settings import Settings
from simai.db.session import get_engine, get_session_factory
from simai.sim.tick import TickDecision, run_tick

sim_app = typer.Typer(help="Comandi di simulazione.")


def _format_decision(d: TickDecision) -> str:
    if d.action is None or d.satisfied is None or d.value_before is None or d.value_after is None:
        return f"  {d.character_key:<10} NESSUNA AZIONE (location={d.location_key})"
    return (
        f"  {d.character_key:<10} {d.action.value.upper():<10} "
        f"{d.satisfied.value.upper():<8} "
        f"{d.value_before:5.1f} -> {d.value_after:5.1f}  "
        f"({d.location_key})"
    )


@sim_app.command("tick")
def tick(
    minutes: int = typer.Option(60, "--minutes", "-m"),
    tick_index: int = typer.Option(0, "--tick"),
    seed: int | None = typer.Option(None, "--seed"),
    include_player: bool = typer.Option(False, "--include-player"),
) -> None:
    """Avanza la simulazione: decadimento, decisione NPC, effetto."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    used_seed = seed if seed is not None else Settings().master_seed

    with factory() as session:
        report = run_tick(
            session,
            minutes=minutes,
            tick_index=tick_index,
            master_seed=used_seed,
            include_player=include_player,
        )
        session.commit()

    typer.echo(f"Tick {report.tick_index} — {report.minutes} minuti (seed {report.seed})")
    for d in report.decisions:
        typer.echo(_format_decision(d))
