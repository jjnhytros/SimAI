import time

import typer
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.cli._helpers import require_schema
from simai.db.session import get_engine, get_session_factory
from simai.mood.service import mood_label
from simai.needs.enums import NeedKind
from simai.needs.service import needs_of
from simai.sim.tick import TickDecision, TickReport, run_tick
from simai.world.models import Character, Location

console = Console()

watch_app = typer.Typer(help="Osserva la simulazione tick-per-tick.")


def _mood_color(mood: float) -> str:
    if mood >= 80:
        return "green"
    if mood >= 60:
        return "cyan"
    if mood >= 40:
        return "yellow"
    if mood >= 20:
        return "orange3"
    return "red"


def _decision_line(d: TickDecision) -> str:
    if d.moved_to is not None:
        return (
            f"[magenta]{d.character_key:<10}[/magenta] "
            f"[bold]MOVE[/bold] {d.moved_from} → {d.moved_to}"
        )
    if d.action is None or d.satisfied is None:
        return f"[dim]{d.character_key:<10} — in attesa[/dim]"
    assert d.value_before is not None and d.value_after is not None
    return (
        f"[bold]{d.character_key:<10}[/bold] "
        f"{d.action.value.upper():<10} "
        f"{d.satisfied.value.upper():<8} "
        f"{d.value_before:5.1f} → {d.value_after:5.1f}"
    )


def _render(
    session: Session,
    report: TickReport,
    last_actions: dict[str, str],
) -> Panel:
    characters = list(session.scalars(select(Character).order_by(Character.id)))
    locations = list(session.scalars(select(Location)))
    loc_by_id = {loc.id: loc for loc in locations}

    title = Text()
    title.append(f"Tick {report.tick_index}  ", style="bold")
    title.append(
        f"({report.minutes} min, seed {report.seed})",
        style="dim",
    )

    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("char", style="bold")
    table.add_column("loc")
    table.add_column("mood", justify="right")
    table.add_column("hunger", justify="right")
    table.add_column("thirst", justify="right")
    table.add_column("fun", justify="right")
    table.add_column("intimacy", justify="right")
    table.add_column("ultima azione")

    for char in characters:
        loc = loc_by_id.get(char.location_id)
        loc_label = loc.key if loc else "?"
        marker = "★ " if char.is_player else "  "
        mood = float(char.mood)
        color = _mood_color(mood)
        needs = needs_of(session, char.id)
        table.add_row(
            f"{marker}{char.key}",
            loc_label,
            f"[{color}]{mood:5.1f}[/{color}] [dim]{mood_label(mood)}[/dim]",
            f"{needs.get(NeedKind.HUNGER, 0):5.1f}",
            f"{needs.get(NeedKind.THIRST, 0):5.1f}",
            f"{needs.get(NeedKind.FUN, 0):5.1f}",
            f"{needs.get(NeedKind.INTIMACY, 0):5.1f}",
            last_actions.get(char.key, "—"),
        )

    decisions_group = Group(
        Text("Decisioni del tick:", style="bold underline"),
        *[Text.from_markup(_decision_line(d)) for d in report.decisions],
    )

    return Panel(
        Group(title, table, Text(""), decisions_group),
        title="SimAI — Quartiere delle Muse",
        border_style="blue",
    )


@watch_app.command("run")
def run(
    ticks: int = typer.Option(20, "--ticks", "-n"),
    minutes: int = typer.Option(60, "--minutes", "-m"),
    delay: float = typer.Option(0.5, "--delay", "-d"),
    include_player: bool = typer.Option(False, "--include-player"),
) -> None:
    """Avvia la simulazione e la mostra tick-per-tick.

    Ctrl+C interrompe in modo pulito dopo il tick corrente; i tick
    completati sono già committati.
    """
    if ticks <= 0:
        typer.echo("--ticks deve essere > 0", err=True)
        raise typer.Exit(code=1)
    if minutes <= 0:
        typer.echo("--minutes deve essere > 0", err=True)
        raise typer.Exit(code=1)
    if delay < 0:
        typer.echo("--delay deve essere >= 0", err=True)
        raise typer.Exit(code=1)

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    last_actions: dict[str, str] = {}

    with factory() as session, Live(console=console, refresh_per_second=10) as live:
        try:
            for _ in range(ticks):
                report = run_tick(
                    session,
                    minutes=minutes,
                    include_player=include_player,
                )
                session.commit()

                for d in report.decisions:
                    if d.moved_to is not None:
                        last_actions[d.character_key] = f"→ {d.moved_to}"
                    elif d.action is not None:
                        last_actions[d.character_key] = d.action.value
                    else:
                        last_actions[d.character_key] = "—"

                live.update(_render(session, report, last_actions))
                if delay > 0:
                    time.sleep(delay)
        except KeyboardInterrupt:
            pass

    console.print("[dim]Watch interrotta. I tick completati sono stati salvati.[/dim]")
