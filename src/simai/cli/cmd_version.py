import typer

from simai.__version__ import __version__


def version_command() -> None:
    """Mostra la versione di SimAI."""
    typer.echo(f"SimAI {__version__}")
