"""Comandi `db`: migrazioni, stato, reset."""

from __future__ import annotations

import typer
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from rich.table import Table
from sqlalchemy import text

from simai.cli._console import console
from simai.config.settings import get_settings
from simai.db.session import get_engine, sqlite_path_from_url

db_app = typer.Typer(
    name="db",
    help="Database e migrazioni.",
    no_args_is_help=True,
)


@db_app.command("upgrade")
def db_upgrade(
    revision: str = typer.Option("head", "--to", help="Revision target."),
) -> None:
    """Applica le migrazioni Alembic (default: head)."""
    cfg = AlembicConfig("alembic.ini")
    alembic_command.upgrade(cfg, revision)
    console.print(f"[green]Migrazioni applicate fino a {revision}.[/]")


@db_app.command("status")
def db_status() -> None:
    """Mostra lo stato del database e delle migrazioni."""
    settings = get_settings()
    db_path = sqlite_path_from_url(settings.db_url)

    table = Table(title="SimAI — DB Status")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("db_url", settings.db_url)
    table.add_row("db_path", str(db_path) if db_path else "n/a")
    table.add_row("db_exists", str(db_path.exists()) if db_path else "n/a")

    alembic_rev: str | None = None
    core_versions: list[tuple[str, str, str]] = []
    if db_path is not None and db_path.exists():
        try:
            engine = get_engine()
            with engine.connect() as conn:
                try:
                    row = conn.execute(text("SELECT version_num FROM alembic_version")).first()
                    alembic_rev = str(row[0]) if row else None
                except Exception:
                    alembic_rev = None
                try:
                    rows = conn.execute(
                        text(
                            "SELECT version, COALESCE(git_sha, ''), applied_at "
                            "FROM core_version ORDER BY applied_at DESC"
                        )
                    ).all()
                    core_versions = [(str(r[0]), str(r[1]), str(r[2])) for r in rows]
                except Exception:
                    core_versions = []
        except Exception as exc:
            console.print(f"[red]Errore apertura DB: {exc}[/]")

    table.add_row("alembic_revision", alembic_rev or "—")
    table.add_row("core_version_rows", str(len(core_versions)))
    console.print(table)

    if core_versions:
        cv_table = Table(title="SimAI — Core Version history")
        cv_table.add_column("Version", style="yellow")
        cv_table.add_column("Git SHA", style="cyan")
        cv_table.add_column("Applied At", style="green")
        for v, sha, at in core_versions:
            cv_table.add_row(v, sha or "—", at)
        console.print(cv_table)


@db_app.command("reset")
def db_reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Conferma senza prompt interattivo."),
    seed: bool = typer.Option(
        False,
        "--seed",
        help="Esegue world+npc+economy seed dopo la migrazione.",
    ),
) -> None:
    """Distrugge e ricrea il DB: cancella il file, riapplica tutte le migrazioni.

    Con `--seed`, esegue in sequenza:
      1. `world seed`  (9 location: 6 casa + 3 negozi + 10 shop items)
      2. `npc seed`    (6 character, relazioni demo)
      3. `economy seed` (assegna jobs a NPC adulti)
    """
    settings = get_settings()
    db_path = sqlite_path_from_url(settings.db_url)
    if db_path is None:
        console.print("[red]`db reset` supportato solo su SQLite file-based.[/]")
        raise typer.Exit(code=1)

    if not yes:
        typer.confirm(
            f"Confermi reset del DB {db_path}? Tutti i dati andranno persi.",
            abort=True,
        )

    for suffix in ("", "-wal", "-shm"):
        p = db_path.with_name(db_path.name + suffix)
        if p.exists():
            p.unlink()
            console.print(f"[dim]Rimosso: {p}[/]")

    cfg = AlembicConfig("alembic.ini")
    alembic_command.upgrade(cfg, "head")
    console.print("[green]DB ricreato e migrato fino a head.[/]")

    if seed:
        # Import locale per evitare dipendenze circolari.
        from simai.cli.cmd_economy import economy_seed
        from simai.cli.cmd_npc import seed_npc_data
        from simai.cli.cmd_world import world_seed

        world_seed()
        count, _ = seed_npc_data(n_random=4)
        if count > 0:
            console.print(f"[green]NPC seed:[/] {count} personaggi creati")
        else:
            console.print("[yellow]NPC già presenti.[/]")
        economy_seed()


def register(app: typer.Typer) -> None:
    """Registra il sub-app `db` sull'app root."""
    app.add_typer(db_app, name="db")
