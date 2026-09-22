"""Helper condivisi tra i comandi CLI."""

from __future__ import annotations

from pathlib import Path

from rich.table import Table
from sqlalchemy import text

from simai.cli._console import console
from simai.config.settings import get_settings
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.core.save_manager import SaveInfo, SaveManager
from simai.db.session import get_engine, sqlite_path_from_url


def extract_sqlite_path(url: str) -> Path | None:
    """Alias retro-compatibile di `sqlite_path_from_url`."""
    return sqlite_path_from_url(url)


def build_starting_datetime() -> AnthalysDateTime:
    """Costruisce l'`AnthalysDateTime` iniziale dalle settings."""
    settings = get_settings()
    return AnthalysDateTime(
        year=settings.starting_year,
        month=settings.starting_month,
        day=settings.starting_day,
    )


def build_save_manager() -> SaveManager:
    """Costruisce un `SaveManager` dalle settings correnti."""
    settings = get_settings()
    db_path = sqlite_path_from_url(settings.db_url)
    return SaveManager(
        saves_dir=settings.saves_dir,
        db_source_path=db_path,
        encryption_key=settings.save_encryption_key,
    )


def check_migrations_applied() -> bool:
    """``True`` se il DB esiste ed ha `alembic_version` popolata."""
    settings = get_settings()
    db_path = sqlite_path_from_url(settings.db_url)
    if db_path is None or not db_path.exists():
        return False
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text("SELECT version_num FROM alembic_version")).first()
            return row is not None
    except Exception:
        return False


def print_save_table(saves: list[SaveInfo]) -> None:
    """Stampa una tabella Rich con l'elenco dei salvataggi."""
    if not saves:
        console.print("[yellow]Nessun salvataggio presente.[/]")
        return
    table = Table(title="SimAI — Salvataggi")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Nome", style="magenta")
    table.add_column("Creato", style="green")
    table.add_column("Versione", style="yellow")
    table.add_column("Tick", justify="right")
    table.add_column("Anthalys", style="blue")
    table.add_column("Size", justify="right")
    table.add_column("Flags")
    for s in saves:
        flags: list[str] = []
        if s.encrypted:
            flags.append("enc")
        if s.compressed:
            flags.append("zstd")
        table.add_row(
            str(s.save_id),
            s.name,
            s.created_at.strftime("%Y-%m-%d %H:%M"),
            s.simai_version,
            str(s.tick_index),
            s.anthalys_datetime or "—",
            f"{s.file_size / 1024:.1f} KiB",
            ",".join(flags) or "—",
        )
    console.print(table)
