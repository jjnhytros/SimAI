"""Comandi `sim`: simulazione headless e tempo."""

from __future__ import annotations

import typer
from rich.table import Table

from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.config.anthalys import (
    DAYS_PER_YEAR,
    HOURS_PER_DAY,
)
from simai.config.settings import get_settings
from simai.core.anthalys_calendar import AnthalysCalendar
from simai.core.event_bus import EventBus
from simai.core.lod import LODLevel
from simai.core.simulation_loop import SimulationLoop
from simai.core.time_manager import TimeManager
from simai.db.session import get_session_factory
from simai.npc import NPCManager
from simai.sim.anthalys.time import (
    AnthalysClock,
    Holiday,
    HolidayRegistry,
    season_info,
)

sim_app = typer.Typer(
    name="sim",
    help="Comandi di simulazione.",
    no_args_is_help=True,
)

time_app = typer.Typer(
    name="time",
    help="Tempo di simulazione (calendario Anthalys).",
    no_args_is_help=True,
)

sim_app.add_typer(time_app, name="time")


# ---------------------------------------------------------------------------
# `sim time`
# ---------------------------------------------------------------------------


@time_app.command("show")
def time_show() -> None:
    """Mostra data/ora iniziale di simulazione e metadati del calendario."""
    dt = build_starting_datetime()
    settings = get_settings()

    table = Table(title="SimAI — Time (start)")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("datetime", str(dt))
    table.add_row("iso", dt.to_iso_string())
    table.add_row("weekday", AnthalysCalendar.weekday_of(dt))
    table.add_row("month_name", AnthalysCalendar.month_name(dt))
    table.add_row("day_of_year", f"{AnthalysCalendar.day_of_year(dt)} / {DAYS_PER_YEAR}")
    table.add_row("season", str(AnthalysCalendar.season_of(dt)))
    table.add_row("phase", str(AnthalysCalendar.phase_of(dt)))
    table.add_row("tick_minutes", str(settings.tick_minutes))
    table.add_row("ticks_per_day", str(HOURS_PER_DAY * 60 // settings.tick_minutes))
    table.add_row(
        "ticks_per_year",
        str(DAYS_PER_YEAR * HOURS_PER_DAY * 60 // settings.tick_minutes),
    )
    console.print(table)


@time_app.command("advance")
def time_advance(
    ticks: int = typer.Argument(..., min=0, help="Tick da avanzare."),
) -> None:
    """Avanza N tick dallo starting datetime e mostra il risultato."""
    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(ticks)
    end = tm.current

    table = Table(title=f"SimAI — Time advance ({ticks} tick)")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("start", str(start))
    table.add_row("end", str(end))
    table.add_row("iso_end", end.to_iso_string())
    table.add_row("elapsed_tick", str(ticks))
    table.add_row("elapsed_minutes", str(ticks * tm.tick_minutes))
    table.add_row(
        "elapsed_days",
        f"{ticks * tm.tick_minutes / (HOURS_PER_DAY * 60):.3f}",
    )
    table.add_row("weekday", AnthalysCalendar.weekday_of(end))
    table.add_row("month_name", AnthalysCalendar.month_name(end))
    table.add_row("day_of_year", f"{AnthalysCalendar.day_of_year(end)} / {DAYS_PER_YEAR}")
    table.add_row("season", str(AnthalysCalendar.season_of(end)))
    table.add_row("phase", str(AnthalysCalendar.phase_of(end)))
    console.print(table)


# ---------------------------------------------------------------------------
# `sim start`
# ---------------------------------------------------------------------------


@sim_app.command("start")
def sim_start(
    max_ticks: int = typer.Option(100, "--max-ticks", "-n", min=1),
    perf_threshold_ms: float = typer.Option(100.0, "--perf-threshold-ms"),
    with_npcs: bool = typer.Option(
        False,
        "--npcs/--no-npcs",
        help="Abilita la simulazione degli NPC (richiede `db upgrade` e `npc seed`).",
    ),
    autosave_every: int = typer.Option(
        0,
        "--autosave-every",
        min=0,
        help="Flush NPC ogni N tick (0 = disabilitato, flush solo a fine loop).",
    ),
    npc_lod: str = typer.Option(
        "FULL",
        "--npc-lod",
        help="LOD di default per gli NPC (FULL/REDUCED/BACKGROUND).",
    ),
    use_bt: bool = typer.Option(
        False,
        "--bt/--no-bt",
        help="Usa il Behaviour Tree per le azioni NPC (sperimentale).",
    ),
) -> None:
    """Avvia la simulazione headless per N tick (opzionalmente con NPC)."""
    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    event_bus = EventBus()

    # --- NPC manager (opzionale) ---
    npc_manager: NPCManager | None = None
    if with_npcs:
        if not check_migrations_applied():
            console.print(
                "[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]"
            )
            raise typer.Exit(code=1)

        try:
            default_lod = LODLevel[npc_lod.upper()]
        except KeyError:
            console.print(f"[red]LOD non valido: {npc_lod!r}. Usa FULL, REDUCED o BACKGROUND.[/]")
            raise typer.Exit(code=1) from None

        from simai.npc import LifecycleManager

        lifecycle = LifecycleManager(
            session_factory=get_session_factory(),
            event_bus=event_bus,
            seed=settings.master_seed + 1,
            master_seed=settings.master_seed,
        )
        npc_manager = NPCManager(
            session_factory=get_session_factory(),
            event_bus=event_bus,
            seed=settings.master_seed,
            autosave_every=autosave_every,
            default_lod=default_lod,
            lifecycle=lifecycle,
            time_provider=lambda: tm.current,
            use_bt=use_bt,
        )

        loaded = npc_manager.load_from_db()
        if loaded == 0:
            console.print("[yellow]Nessun NPC nel DB. Esegui `npc seed` prima.[/]")
            raise typer.Exit(code=1)
        console.print(f"[green]Caricati {loaded} NPC[/] (LOD default: {default_lod.name}).")

    # --- Loop ---
    loop = SimulationLoop(
        time_manager=tm,
        event_bus=event_bus,
        npc_manager=npc_manager,
        perf_threshold_ms=perf_threshold_ms,
    )
    executed = loop.run_for(max_ticks)

    # --- Flush finale ---
    flush_count = 0
    if npc_manager is not None:
        flush_count = npc_manager.flush()

    end = tm.current
    last = loop.last_report

    table = Table(title=f"SimAI — sim start ({executed} tick eseguiti)")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("start", str(start))
    table.add_row("end", str(end))
    table.add_row("tick_minutes", str(tm.tick_minutes))
    table.add_row("ticks_requested", str(max_ticks))
    table.add_row("ticks_executed", str(executed))
    table.add_row("paused", str(loop.paused))
    table.add_row("speed", str(loop.speed))
    table.add_row("events_processed_total", str(event_bus.stats_processed))
    if last is not None:
        table.add_row("last_tick_ms", f"{last.duration_ms:.3f}")
        table.add_row("last_tick_time", last.time_advanced_to)

    if npc_manager is not None:
        stats = npc_manager.stats()
        table.add_row("npcs_total", str(stats["total"]))
        table.add_row("npcs_simulated", str(stats["simulated"]))
        table.add_row(
            "npcs_by_lod",
            f"F={stats['full']} R={stats['reduced']} B={stats['background']}",
        )
        table.add_row("npcs_flushed_final", str(flush_count))
        table.add_row("npcs_flush_calls", str(stats["flush_count"]))
        table.add_row("npcs_use_bt", str(stats["use_bt"]))
        table.add_row("npcs_skills_total", str(stats["total_skills"]))
        table.add_row("npcs_skills_dirty", str(stats["dirty_skills"]))

    table.add_row("weekday", AnthalysCalendar.weekday_of(end))
    table.add_row("season", str(AnthalysCalendar.season_of(end)))
    table.add_row("phase", str(AnthalysCalendar.phase_of(end)))
    console.print(table)


# ---------------------------------------------------------------------------
# `sim time moons`
# ---------------------------------------------------------------------------


@time_app.command("moons")
def time_moons(
    at_tick: int = typer.Option(0, "--at-tick", "-n", min=0),
) -> None:
    """Mostra la fase corrente delle 3 lune di Anthalys a `at_tick` tick dallo start."""
    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    clock = AnthalysClock(tm, master_seed=settings.master_seed)

    clock.advance_ticks(at_tick)
    phases = clock.current_moon_phases()
    progresses = clock.moons.all_progress(clock.current)

    table = Table(title=f"SimAI — Fasi lunari @ {clock.current}")
    table.add_column("Luna", style="cyan")
    table.add_column("Periodo (gg)", justify="right")
    table.add_column("Progresso", justify="right")
    table.add_column("Fase", style="magenta")
    for moon in clock.moons.moons:
        table.add_row(
            moon.name,
            str(moon.orbital_period_days),
            f"{progresses[moon.name]:.3f}",
            str(phases[moon.name]),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# `sim time holidays`
# ---------------------------------------------------------------------------


def _print_holiday_list(holidays: list[Holiday]) -> None:
    if not holidays:
        console.print("[yellow]Nessuna festività.[/]")
        return
    table = Table(title="SimAI — Festività")
    table.add_column("Nome", style="cyan")
    table.add_column("Tipo", style="yellow")
    table.add_column("Mese/Giorno", justify="right")
    table.add_column("Descrizione", style="magenta")
    for h in holidays:
        when = f"{h.month:02d}/{h.day:02d}" if h.is_fixed else "mobile"
        table.add_row(h.name, "fissa" if h.is_fixed else "mobile", when, h.description)
    console.print(table)


@time_app.command("holidays")
def time_holidays() -> None:
    """Elenca tutte le festività (fisse e mobili)."""
    _print_holiday_list(list(HolidayRegistry.default().holidays))


# ---------------------------------------------------------------------------
# `sim time upcoming-holidays`
# ---------------------------------------------------------------------------


@time_app.command("upcoming-holidays")
def time_upcoming_holidays(
    days: int = typer.Option(200, "--days", "-d", min=1),
) -> None:
    """Prossime festività entro `days` giorni Anthalys dallo start."""
    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    clock = AnthalysClock(tm, master_seed=settings.master_seed)

    holidays_registry = clock.holidays
    moons = clock.moons
    current = clock.current

    table = Table(title=f"SimAI — Prossime festività (entro {days} gg)")
    table.add_column("Data", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="yellow")
    count = 0
    for _ in range(days):
        current = current.add_minutes(28 * 60)
        matches = holidays_registry.on_date(current, moons)
        for h in matches:
            table.add_row(str(current), h.name, "fissa" if h.is_fixed else "mobile")
            count += 1
    if count == 0:
        console.print(f"[yellow]Nessuna festività nei prossimi {days} giorni.[/]")
        return
    console.print(table)


# ---------------------------------------------------------------------------
# `sim time season`
# ---------------------------------------------------------------------------


@time_app.command("season")
def time_season(
    at_tick: int = typer.Option(0, "--at-tick", "-n", min=0),
) -> None:
    """Dettagli della stagione corrente a `at_tick` tick dallo start."""
    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    info = season_info(tm.current)

    table = Table(title=f"SimAI — Stagione @ {tm.current}")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("datetime", str(tm.current))
    table.add_row("season", str(info.season))
    table.add_row("day_of_season", f"{info.day_of_season} / 108")
    table.add_row("days_remaining", str(info.days_remaining))
    table.add_row("progress", f"{info.progress:.3f}")
    table.add_row("next_season", str(info.next_season))
    console.print(table)


# ---------------------------------------------------------------------------
# `sim time astro`
# ---------------------------------------------------------------------------


@time_app.command("astro")
def time_astro(
    horizon_days: int = typer.Option(2000, "--horizon", "-H", min=1),
) -> None:
    """Prossimi eventi astronomici (eclissi, comete, meteore) entro `horizon_days`."""
    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    clock = AnthalysClock(tm, master_seed=settings.master_seed)

    events = clock.next_astro_events(horizon_days=horizon_days)
    if not events:
        console.print(f"[yellow]Nessun evento astronomico entro {horizon_days} giorni.[/]")
        return

    table = Table(title="SimAI — Prossimi eventi astronomici")
    table.add_column("Data", style="cyan")
    table.add_column("Tipo", style="yellow")
    table.add_column("Descrizione", style="magenta")
    for e in events:
        table.add_row(str(e.datetime), str(e.type), e.description)
    console.print(table)


def register(app: typer.Typer) -> None:
    """Registra il sub-app `sim` sull'app root."""
    app.add_typer(sim_app, name="sim")
