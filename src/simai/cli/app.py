import typer

from simai.cli.cmd_db import db_app
from simai.cli.cmd_i18n import i18n_app
from simai.cli.cmd_version import version_command
from simai.cli.cmd_world import world_app

app = typer.Typer(
    name="simai",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def callback() -> None:
    """SimAI — motore di simulazione della vita di Anthalys."""


app.command("version")(version_command)
app.add_typer(db_app, name="db")
app.add_typer(i18n_app, name="i18n")
app.add_typer(world_app, name="world")


def main() -> None:
    app()
