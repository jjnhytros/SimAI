"""Comandi `stats`: statistiche popolazione e censimenti."""

from __future__ import annotations

import typer
from rich.table import Table

from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.config.settings import get_settings
from simai.core.anthalys_datetime import AnthalysDateTime  # ← aggiunto
from simai.core.time_manager import TimeManager
from simai.db.session import get_session_factory
from simai.npc.stats import PopulationStatsService

stats_app = typer.Typer(
    name="stats",
    help="Statistiche popolazione e censimenti.",
    no_args_is_help=True,
)


def _require_migrated() -> None:
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)


def _resolve_datetime(at_tick: int) -> AnthalysDateTime:
    settings = get_settings()
    tm = TimeManager(start=build_starting_datetime(), tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    return tm.current


# ---------------------------------------------------------------------------
# population
# ---------------------------------------------------------------------------


@stats_app.command("population")
def stats_population(
    at_tick: int = typer.Option(
        0,
        "--at-tick",
        "-t",
        min=0,
        help="Tick di riferimento (default: 0).",
    ),
) -> None:
    """Snapshot live della popolazione al tick dato."""
    _require_migrated()
    current = _resolve_datetime(at_tick)

    factory = get_session_factory()
    with factory() as session:
        stats = PopulationStatsService.live_stats(session, current)

    console.print(f"[bold]Statistiche popolazione @ {current}[/]")

    summary = Table(title="Riepilogo")
    summary.add_column("Chiave", style="cyan")
    summary.add_column("Valore", style="magenta", justify="right")
    summary.add_row("total_alive", str(stats.total_alive))
    summary.add_row("total_dead", str(stats.total_dead))
    summary.add_row("total_male", str(stats.total_male))
    summary.add_row("total_female", str(stats.total_female))
    summary.add_row("total_intersex", str(stats.total_intersex))
    summary.add_row("births_this_month", str(stats.births_current_month))
    summary.add_row("deaths_this_month", str(stats.deaths_current_month))
    console.print(summary)

    ped_table = Table(title="Per fascia pediatrica (vivi)")
    ped_table.add_column("Fascia", style="cyan")
    ped_table.add_column("N", justify="right", style="magenta")
    for stage, n in stats.pediatric_breakdown.items():
        if n > 0:
            ped_table.add_row(stage, str(n))
    console.print(ped_table)

    psy_table = Table(title="Per fascia psicosociale (vivi)")
    psy_table.add_column("Fascia", style="cyan")
    psy_table.add_column("N", justify="right", style="magenta")
    for stage, n in stats.psychosocial_breakdown.items():
        if n > 0:
            psy_table.add_row(stage, str(n))
    console.print(psy_table)


# ---------------------------------------------------------------------------
# snapshot
# ---------------------------------------------------------------------------


@stats_app.command("snapshot")
def stats_snapshot(
    at_tick: int = typer.Option(
        0,
        "--at-tick",
        "-t",
        min=0,
        help="Tick di riferimento (default: 0).",
    ),
) -> None:
    """Forza un census del mese corrente (upsert)."""
    _require_migrated()
    current = _resolve_datetime(at_tick)

    factory = get_session_factory()
    with factory() as session:
        census = PopulationStatsService.snapshot(session, current)
        session.commit()

    table = Table(title=f"Census {census.year}-{census.month:02d}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("total_alive", str(census.total_alive))
    table.add_row("total_male", str(census.total_male))
    table.add_row("total_female", str(census.total_female))
    table.add_row("total_intersex", str(census.total_intersex))
    table.add_row("births_this_month", str(census.births_this_month))
    table.add_row("deaths_this_month", str(census.deaths_this_month))
    console.print(table)


# ---------------------------------------------------------------------------
# census
# ---------------------------------------------------------------------------


@stats_app.command("census")
def stats_census(
    year: int | None = typer.Option(None, "--year", "-y", help="Filtra per anno Anthalys."),
    limit: int = typer.Option(
        24,
        "--limit",
        "-l",
        min=1,
        max=500,
        help="Numero massimo di righe (default: 24 mesi).",
    ),
) -> None:
    """Storico dei censimenti mensili."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        rows = PopulationStatsService.census_history(session, year=year, limit=limit)

    if not rows:
        console.print("[yellow]Nessun census registrato.[/]")
        console.print(
            "[dim]Il census viene creato automaticamente al cambio mese "
            "durante la simulazione, o manualmente con `stats snapshot`.[/]"
        )
        return

    title = f"Censimenti (anno {year})" if year is not None else "Censimenti (ultimi)"
    table = Table(title=title)
    table.add_column("Anno", style="cyan", justify="right")
    table.add_column("Mese", justify="right")
    table.add_column("Vivi", justify="right", style="green")
    table.add_column("M", justify="right")
    table.add_column("F", justify="right")
    table.add_column("I", justify="right")
    table.add_column("Nati", justify="right", style="yellow")
    table.add_column("Morti", justify="right", style="red")
    for c in rows:
        table.add_row(
            str(c.year),
            str(c.month),
            str(c.total_alive),
            str(c.total_male),
            str(c.total_female),
            str(c.total_intersex),
            str(c.births_this_month),
            str(c.deaths_this_month),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# year-summary
# ---------------------------------------------------------------------------


@stats_app.command("year-summary")
def stats_year_summary(
    year: int = typer.Argument(..., help="Anno Anthalys."),
) -> None:
    """Riepilogo annuale aggregato dai census mensili."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        rows = PopulationStatsService.census_history(session, year=year)

    if not rows:
        console.print(f"[yellow]Nessun census per l'anno {year}.[/]")
        return

    # Ordina per mese crescente
    ordered = sorted(rows, key=lambda c: c.month)
    total_births = sum(c.births_this_month for c in ordered)
    total_deaths = sum(c.deaths_this_month for c in ordered)
    avg_alive = sum(c.total_alive for c in ordered) // len(ordered)
    first = ordered[0]
    last = ordered[-1]

    table = Table(title=f"Riepilogo anno {year}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("census_months", str(len(ordered)))
    table.add_row("births_total", str(total_births))
    table.add_row("deaths_total", str(total_deaths))
    table.add_row("net_change", f"{total_births - total_deaths:+d}")
    table.add_row("alive_first_month", str(first.total_alive))
    table.add_row("alive_last_month", str(last.total_alive))
    table.add_row("alive_avg", str(avg_alive))
    console.print(table)


def register(app: typer.Typer) -> None:
    """Registra il sub-app `stats` sull'app root."""
    app.add_typer(stats_app, name="stats")
