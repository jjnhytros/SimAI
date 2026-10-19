import typer

from simai.cli._helpers import require_schema
from simai.db.session import get_engine, get_session_factory
from simai.sim.loop import run_simulation
from simai.sim.state import get_state, reset_state
from simai.sim.tick import TickDecision, TickReport, run_tick

sim_app = typer.Typer(help="Comandi di simulazione.")


def _format_decision(d: TickDecision) -> str:
    if d.action is None or d.satisfied is None:
        return f"  {d.character_key:<10} NESSUNA AZIONE (location={d.location_key})"
    assert d.value_before is not None and d.value_after is not None
    base = (
        f"  {d.character_key:<10} {d.action.value.upper():<10} "
        f"{d.satisfied.value.upper():<8} "
        f"{d.value_before:5.1f} -> {d.value_after:5.1f}  "
        f"({d.location_key})"
    )
    if d.relationship_strength_after is not None:
        base += f"  [rel → {d.relationship_strength_after:.1f}]"
    return base


@sim_app.command("tick")
def tick(
    minutes: int = typer.Option(60, "--minutes", "-m"),
    tick_index: int | None = typer.Option(None, "--tick"),
    seed: int | None = typer.Option(None, "--seed"),
    include_player: bool = typer.Option(False, "--include-player"),
) -> None:
    """Avanza la simulazione di un tick."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    with factory() as session:
        report = run_tick(
            session,
            minutes=minutes,
            tick_index=tick_index,
            master_seed=seed,
            include_player=include_player,
        )
        session.commit()

    typer.echo(f"Tick {report.tick_index} — {report.minutes} minuti (seed {report.seed})")
    for d in report.decisions:
        typer.echo(_format_decision(d))


@sim_app.command("run")
def run(
    ticks: int = typer.Option(10, "--ticks", "-n"),
    minutes: int = typer.Option(60, "--minutes", "-m"),
    autosave_every: int = typer.Option(0, "--autosave-every"),
    autosave_name: str = typer.Option("autosave", "--autosave-name"),
    include_player: bool = typer.Option(False, "--include-player"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
) -> None:
    """Esegue N tick consecutivi con autosave opzionale."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    def on_tick(report: TickReport) -> None:
        if quiet:
            return
        typer.echo(f"Tick {report.tick_index} — {report.minutes}m ({len(report.decisions)} NPC)")

    with factory() as session:
        try:
            report = run_simulation(
                session,
                ticks=ticks,
                minutes_per_tick=minutes,
                autosave_every=autosave_every,
                autosave_name=autosave_name,
                include_player=include_player,
                on_tick=on_tick,
            )
        except ValueError as exc:
            typer.echo(f"Errore: {exc}", err=True)
            raise typer.Exit(code=1) from exc

    if report.failed_at_tick is not None:
        typer.echo(
            f"ERRORE al tick {report.failed_at_tick}: {report.error_message}",
            err=True,
        )
        typer.echo(
            f"Eseguiti {report.ticks_executed} tick prima del fallimento.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(
        f"Eseguiti {report.ticks_executed} tick "
        f"da tick {report.started_at_tick} a {report.ended_at_tick} "
        f"({report.total_minutes} minuti simulati)"
    )
    if report.autosaves:
        typer.echo(f"Autosave ({len(report.autosaves)}):")
        for a in report.autosaves:
            if a.error is not None:
                typer.echo(f"  tick {a.tick}: ERRORE {a.error}", err=True)
            elif a.path is not None:
                typer.echo(f"  tick {a.tick}: {a.path}")


@sim_app.command("state")
def state() -> None:
    """Mostra lo stato persistente di simulazione."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        s = get_state(session)
        session.commit()
        typer.echo(f"tick_index: {s.tick_index}")
        typer.echo(f"master_seed: {s.master_seed}")


@sim_app.command("reset")
def reset(
    seed: int = typer.Option(42, "--seed"),
) -> None:
    """Azzera lo stato di simulazione con il seed indicato."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        reset_state(session, master_seed=seed)
        session.commit()
    typer.echo("Stato di simulazione azzerato.")
    typer.echo("tick_index: 0")
    typer.echo(f"master_seed: {seed}")
