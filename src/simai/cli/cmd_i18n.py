import typer

from simai.i18n.checker import check

i18n_app = typer.Typer(help="Comandi i18n.")


@i18n_app.command("check")
def check_command() -> None:
    """Verifica la parità delle chiavi fra i file di locale."""
    problems = check()
    if problems:
        for p in problems:
            typer.echo(f"✗ {p}", err=True)
        raise typer.Exit(code=1)
    typer.echo("✓ i18n OK")
