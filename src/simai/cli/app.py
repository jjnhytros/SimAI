import typer

from simai.cli.cmd_actions import actions_app
from simai.cli.cmd_db import db_app
from simai.cli.cmd_i18n import i18n_app
from simai.cli.cmd_needs import needs_app
from simai.cli.cmd_relationships import relationships_app
from simai.cli.cmd_save import save_app
from simai.cli.cmd_sim import sim_app
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
app.add_typer(needs_app, name="needs")
app.add_typer(actions_app, name="actions")
app.add_typer(sim_app, name="sim")
app.add_typer(relationships_app, name="relationships")
app.add_typer(save_app, name="save")


def main() -> None:
    app()
