from pathlib import Path

import typer

from simai.cli._helpers import require_schema
from simai.db.session import get_engine, get_session_factory
from simai.sim.benchmark import format_report, run_benchmark
from simai.sim.loop import run_simulation
from simai.sim.state import get_state, reset_state
from simai.sim.tick import TickDecision, TickReport, run_tick

sim_app = typer.Typer(help="Comandi di simulazione.")


def _format_decision(d: TickDecision) -> str:
    if d.moved_to is not None:
        return f"  {d.character_key:<10} MOVE       {d.moved_from} → {d.moved_to}"
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
    if d.cost_paid > 0:
        base += f"  [-{d.cost_paid:.0f}A]"
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
    if report.payday_count > 0:
        typer.echo(f"💰 Payday: {report.payday_count} personaggi pagati")
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
        payday_note = " 💰" if report.payday_count > 0 else ""
        typer.echo(
            f"Tick {report.tick_index} — {report.minutes}m "
            f"({len(report.decisions)} NPC){payday_note}"
        )

    with factory() as session:
        try:
            run_report = run_simulation(
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

    if run_report.failed_at_tick is not None:
        typer.echo(
            f"ERRORE al tick {run_report.failed_at_tick}: {run_report.error_message}",
            err=True,
        )
        typer.echo(
            f"Eseguiti {run_report.ticks_executed} tick prima del fallimento.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(
        f"Eseguiti {run_report.ticks_executed} tick "
        f"da tick {run_report.started_at_tick} "
        f"a {run_report.ended_at_tick} "
        f"({run_report.total_minutes} minuti simulati)"
    )
    if run_report.total_paydays > 0:
        typer.echo(f"Payday totali nel run: {run_report.total_paydays}")
    if run_report.autosaves:
        typer.echo(f"Autosave ({len(run_report.autosaves)}):")
        for a in run_report.autosaves:
            if a.error is not None:
                typer.echo(
                    f"  tick {a.tick}: ERRORE {a.error}",
                    err=True,
                )
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


@sim_app.command("benchmark")
def benchmark(
    years: float = typer.Option(1.0, "--years", "-y"),
    minutes: int = typer.Option(60, "--minutes", "-m"),
    seed: int = typer.Option(42, "--seed"),
    include_player: bool = typer.Option(False, "--include-player"),
    sample_every: int = typer.Option(24, "--sample-every"),
    db: Path | None = typer.Option(None, "--db"),
    output: Path | None = typer.Option(None, "--output", "-o"),
) -> None:
    """Esegue una simulazione accelerata su DB temporaneo."""
    from datetime import UTC, datetime

    db_path = db or Path(f"data/benchmark/bench_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.db")
    try:
        report = run_benchmark(
            db_path,
            years=years,
            minutes_per_tick=minutes,
            seed=seed,
            include_player=include_player,
            sample_every=sample_every,
        )
    except ValueError as exc:
        typer.echo(f"Errore: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(format_report(report))

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.to_json(), encoding="utf-8")
        typer.echo(f"\nReport salvato: {output}")

    if not report.invariants_ok:
        raise typer.Exit(code=1)
