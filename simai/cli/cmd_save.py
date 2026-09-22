"""Comandi `save`: creazione, lista, caricamento, eliminazione, chiave."""

from __future__ import annotations

import importlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import typer

from simai.cli._console import console
from simai.cli._helpers import (
    build_save_manager,
    build_starting_datetime,
    print_save_table,
)
from simai.config.settings import get_settings
from simai.core.save_manager import (
    SaveError,
    SaveFormatError,
    SaveNotFoundError,
)
from simai.core.time_manager import TimeManager
from simai.db.session import get_engine, sqlite_path_from_url
from simai.utils.git import get_git_sha

save_app = typer.Typer(
    name="save",
    help="Gestione salvataggi.",
    no_args_is_help=True,
)


@save_app.command("list")
def save_list() -> None:
    """Elenca tutti i salvataggi disponibili."""
    try:
        sm = build_save_manager()
    except SaveError as exc:
        console.print(f"[red]Errore inizializzazione SaveManager: {exc}[/]")
        raise typer.Exit(code=1) from exc
    print_save_table(sm.list_saves())


@save_app.command("create")
def save_create(
    name: str = typer.Argument(..., help="Nome del salvataggio."),
    tick_index: int = typer.Option(0, "--tick", help="Tick index da registrare."),
) -> None:
    """Crea un nuovo salvataggio dal DB corrente."""
    settings = get_settings()
    db_path = sqlite_path_from_url(settings.db_url)
    if db_path is not None and not db_path.exists():
        console.print(
            f"[yellow]DB non trovato:[/] {db_path}\n"
            "[yellow]Esegui prima:[/] [bold]uv run python -m simai db upgrade[/]"
        )
        raise typer.Exit(code=1)

    try:
        sm = build_save_manager()
    except SaveError as exc:
        console.print(f"[red]Errore inizializzazione SaveManager: {exc}[/]")
        raise typer.Exit(code=1) from exc

    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(tick_index)

    try:
        info = sm.create_save(
            name,
            seed=settings.master_seed,
            tick_index=tick_index,
            anthalys_datetime=tm.current.to_iso_string(),
            git_sha=get_git_sha(),
        )
    except SaveError as exc:
        console.print(f"[red]Errore creazione salvataggio: {exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Salvataggio creato:[/] id={info.save_id} "
        f"name={info.name!r} size={info.file_size} B "
        f"path={info.file_path}"
    )
    console.print(f"[dim]Per caricarlo: uv run python -m simai save load {info.save_id}[/]")


@save_app.command("load")
def save_load(
    save_id: int = typer.Argument(..., help="ID del salvataggio."),
    target: Path | None = typer.Option(
        None,
        "--target",
        "-t",
        help="Path DB di destinazione (default: saves/loaded_<id>.db).",
    ),
) -> None:
    """Ripristina un salvataggio su un DB SQLite."""
    try:
        sm = build_save_manager()
    except SaveError as exc:
        console.print(f"[red]Errore inizializzazione SaveManager: {exc}[/]")
        raise typer.Exit(code=1) from exc

    try:
        state = sm.load_save(save_id, target_db_path=target)
    except SaveNotFoundError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc
    except (SaveError, SaveFormatError) as exc:
        console.print(f"[red]Errore caricamento: {exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Caricato:[/] id={state.info.save_id} name={state.info.name!r} db={state.db_path}"
    )


@save_app.command("delete")
def save_delete(
    save_id: int = typer.Argument(..., help="ID del salvataggio."),
) -> None:
    """Elimina un salvataggio."""
    try:
        sm = build_save_manager()
    except SaveError as exc:
        console.print(f"[red]Errore inizializzazione SaveManager: {exc}[/]")
        raise typer.Exit(code=1) from exc
    try:
        sm.delete_save(save_id)
    except SaveNotFoundError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Eliminato:[/] id={save_id}")


@save_app.command("gen-key")
def save_gen_key() -> None:
    """Genera una chiave Fernet per cifrare i salvataggi."""
    try:
        fernet_module: Any = importlib.import_module("cryptography.fernet")
    except ImportError:
        console.print("[red]cryptography non installato. Installa con: uv sync --extra save[/]")
        raise typer.Exit(code=1) from None
    key: str = fernet_module.Fernet.generate_key().decode("ascii")
    console.print(f"[bold green]SIMAI_SAVE_ENCRYPTION_KEY={key}[/]")


# ---------------------------------------------------------------------------
# restore
# ---------------------------------------------------------------------------


@save_app.command("restore")
def save_restore(
    save_id: int = typer.Argument(..., help="ID del salvataggio."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Conferma senza prompt."),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Crea un backup del DB corrente prima di sovrascriverlo.",
    ),
    keep_loaded: bool = typer.Option(
        False,
        "--keep-loaded",
        help="Mantieni il file `loaded_<id>.db` dopo il restore.",
    ),
) -> None:
    """Ripristina il DB attivo da un salvataggio `.sav`.

    Sequenza:
      1. Carica il `.sav` in `data/saves/loaded_<id>.db`
      2. Chiude le connessioni SQLAlchemy al DB corrente (engine.dispose)
      3. Backup opzionale del DB corrente (`<db>.bak.YYYYMMDD_HHMMSS`)
      4. Sostituisce il DB corrente con quello caricato
      5. (Opzionale) rimuove il file temporaneo `loaded_<id>.db`
    """
    settings = get_settings()
    current_db = sqlite_path_from_url(settings.db_url)
    if current_db is None:
        console.print("[red]`save restore` supportato solo su SQLite file-based.[/]")
        raise typer.Exit(code=1)

    if not yes:
        typer.confirm(
            f"Confermi restore dal salvataggio {save_id}? "
            f"Il DB corrente ({current_db}) sarà sovrascritto.",
            abort=True,
        )

    # 1. Carica il .sav in loaded_<id>.db
    try:
        sm = build_save_manager()
    except SaveError as exc:
        console.print(f"[red]Errore inizializzazione SaveManager: {exc}[/]")
        raise typer.Exit(code=1) from exc

    try:
        state = sm.load_save(save_id)
    except SaveNotFoundError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc
    except (SaveError, SaveFormatError) as exc:
        console.print(f"[red]Errore caricamento: {exc}[/]")
        raise typer.Exit(code=1) from exc

    loaded_path = state.db_path
    if not loaded_path.exists():
        console.print(f"[red]File caricato mancante: {loaded_path}[/]")
        raise typer.Exit(code=1)

    # 2. Dispose engine (chiude connessioni aperte al DB corrente)
    try:
        get_engine().dispose()
    except Exception as exc:
        console.print(f"[yellow]Warning: engine.dispose() fallito: {exc}[/]")

    # 3. Backup
    backup_path: Path | None = None
    if backup and current_db.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = current_db.with_name(f"{current_db.name}.bak.{ts}")
        try:
            shutil.copy2(current_db, backup_path)
            console.print(f"[green]Backup creato:[/] {backup_path}")
        except OSError as exc:
            console.print(f"[red]Backup fallito: {exc}[/]")
            raise typer.Exit(code=1) from exc

    # 4. Rimuovi WAL/SHM del DB corrente (SQLite journal)
    for suffix in ("-wal", "-shm"):
        p = current_db.with_name(current_db.name + suffix)
        if p.exists():
            try:
                p.unlink()
            except OSError as exc:
                console.print(f"[yellow]Warning rimozione {p}: {exc}[/]")

    # 5. Sostituisci il DB corrente
    try:
        shutil.copy2(loaded_path, current_db)
    except OSError as exc:
        console.print(f"[red]Copia DB fallita: {exc}[/]")
        if backup_path is not None:
            console.print(f"[yellow]Il DB originale è salvato in: {backup_path}[/]")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]DB ripristinato:[/] {loaded_path.name} → {current_db}")

    # 6. Rimuovi file temporaneo
    if not keep_loaded and loaded_path.exists():
        try:
            loaded_path.unlink()
            console.print(f"[dim]Rimosso file temporaneo: {loaded_path}[/]")
        except OSError:
            pass

    console.print("[bold green]Restore completato.[/]")
    if backup_path is not None:
        console.print(f"[dim]Per ripristinare il DB precedente: cp {backup_path} {current_db}[/]")


def register(app: typer.Typer) -> None:
    """Registra il sub-app `save` sull'app root."""
    app.add_typer(save_app, name="save")
