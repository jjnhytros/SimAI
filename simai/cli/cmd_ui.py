"""Comandi `ui`: avvio server web (FastAPI + Uvicorn)."""

from __future__ import annotations

import typer

from simai.cli._console import console

ui_app = typer.Typer(
    name="ui",
    help="Server UI web (read-only).",
    no_args_is_help=True,
)


@ui_app.command("serve")
def ui_serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host di bind."),
    port: int = typer.Option(8000, "--port", "-p", min=1, max=65535),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload su modifica (dev)."),
    open_browser: bool = typer.Option(False, "--open", "-o", help="Apri il browser."),
) -> None:
    """Avvia il server UI web."""
    try:
        import uvicorn
    except ImportError:
        console.print(
            "[red]FastAPI/Uvicorn non installati.[/]\n"
            "[yellow]Installa con:[/] [bold]uv sync --extra ui[/]"
        )
        raise typer.Exit(code=1) from None

    from simai.ui.app import create_app

    app = create_app()

    url = f"http://{host}:{port}"
    console.print(f"[green]SimAI UI:[/] {url}")
    console.print("[dim]UI read-only. Avanza la simulazione con la CLI in un'altra shell.[/]")

    if open_browser:
        import webbrowser

        webbrowser.open(url)

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def register(app: typer.Typer) -> None:
    """Registra il sub-app `ui` sull'app root."""
    app.add_typer(ui_app, name="ui")
