import typer

from simai.__version__ import __version__

app = typer.Typer(
    name="simai",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def callback() -> None:
    """SimAI — motore di simulazione della vita di Anthalys."""


@app.command()
def version() -> None:
    """Mostra la versione di SimAI."""
    typer.echo(f"SimAI {__version__}")


def main() -> None:
    app()