"""Entrypoint CLI SimAI — root app, `version`/`info`, register sub-apps."""

from __future__ import annotations

import platform
import sys

import typer
from rich.table import Table

from simai.__version__ import __version__
from simai.cli import (
    cmd_city,
    cmd_db,
    cmd_economy,
    cmd_npc,
    cmd_save,
    cmd_sim,
    cmd_stats,
    cmd_transport,
    cmd_ui,
    cmd_world,
)
from simai.cli._console import console
from simai.cli._helpers import extract_sqlite_path
from simai.config.anthalys import (
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    HOURS_PER_DAY,
    MONTHS,
    MONTHS_PER_YEAR,
    SEASONS,
    WEEKDAYS,
)
from simai.config.settings import get_settings
from simai.utils.git import get_git_sha

app = typer.Typer(
    name="simai",
    help="SimAI — Simulazione di Anthalys.",
    no_args_is_help=True,
    add_completion=False,
)


# ---------------------------------------------------------------------------
# Top-level: version, info
# ---------------------------------------------------------------------------


@app.command()
def version() -> None:
    """Mostra versione SimAI, versione Python e stato del database."""
    settings = get_settings()
    db_path = extract_sqlite_path(settings.db_url)
    if db_path is None:
        db_status = "n/a (non-file URL)"
    elif db_path.exists():
        db_status = f"presente ({db_path})"
    else:
        db_status = f"assente ({db_path})"

    table = Table(title="SimAI — Version")
    table.add_column("Voce", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("SimAI", __version__)
    table.add_row(
        "Python",
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )
    table.add_row("Platform", platform.platform())
    table.add_row("DB URL", settings.db_url)
    table.add_row("DB", db_status)
    table.add_row("Git SHA", get_git_sha(short=True) or "n/a")
    console.print(table)


@app.command()
def info() -> None:
    """Informazioni sull'ambiente SimAI (path, tick rate, calendario)."""
    settings = get_settings()

    env_table = Table(title="SimAI — Ambiente")
    env_table.add_column("Chiave", style="cyan", no_wrap=True)
    env_table.add_column("Valore", style="magenta")
    env_table.add_row("env", settings.env)
    env_table.add_row("debug", str(settings.debug))
    env_table.add_row("log_level", settings.log_level)
    env_table.add_row("master_seed", str(settings.master_seed))
    env_table.add_row("tick_minutes", str(settings.tick_minutes))
    env_table.add_row("data_dir", str(settings.data_dir.resolve()))
    env_table.add_row("saves_dir", str(settings.saves_dir.resolve()))
    env_table.add_row("logs_dir", str(settings.logs_dir.resolve()))
    env_table.add_row("exports_dir", str(settings.exports_dir.resolve()))
    env_table.add_row("ui_enabled", str(settings.ui_enabled))
    env_table.add_row("save_encryption", "on" if settings.save_encryption_key else "off")
    console.print(env_table)

    cal_table = Table(title="SimAI — Calendario Anthalys")
    cal_table.add_column("Chiave", style="cyan", no_wrap=True)
    cal_table.add_column("Valore", style="magenta")
    cal_table.add_row("starting_year", str(settings.starting_year))
    cal_table.add_row("days_per_year", str(DAYS_PER_YEAR))
    cal_table.add_row("months_per_year", str(MONTHS_PER_YEAR))
    cal_table.add_row("days_per_month", str(DAYS_PER_MONTH))
    cal_table.add_row("hours_per_day", str(HOURS_PER_DAY))
    cal_table.add_row("weekdays", ", ".join(WEEKDAYS))
    cal_table.add_row("months", ", ".join(MONTHS))
    cal_table.add_row("seasons", ", ".join(SEASONS))
    console.print(cal_table)


# ---------------------------------------------------------------------------
# Register sub-apps
# ---------------------------------------------------------------------------

cmd_sim.register(app)
cmd_db.register(app)
cmd_save.register(app)
cmd_world.register(app)
cmd_npc.register(app)
cmd_economy.register(app)
cmd_stats.register(app)
cmd_ui.register(app)
cmd_city.register(app)
cmd_transport.register(app)


if __name__ == "__main__":  # pragma: no cover
    app()
