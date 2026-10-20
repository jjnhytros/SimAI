import typer

from simai.actions.do import do_action
from simai.actions.enums import ActionKind
from simai.cli._helpers import require_schema
from simai.db.session import get_engine, get_session_factory
from simai.mood.service import mood_label
from simai.needs.enums import NeedKind
from simai.player.status import build_player_status
from simai.world.move import move_character

player_app = typer.Typer(help="Comandi del giocatore.")


@player_app.command("status")
def status() -> None:
    """Mostra il pannello unificato del giocatore."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        s = build_player_status(session)
    if s is None:
        typer.echo("Nessun player nel mondo. Esegui `simai world seed`.")
        raise typer.Exit(code=1)

    typer.echo(f"Tick: {s.tick_index} (seed {s.master_seed})")
    typer.echo(f"Player: {s.name} ({s.character_key}), {s.age_years} anni")
    typer.echo(f"Umore: {s.mood:.1f} ({mood_label(s.mood)})")
    typer.echo(f"Location: {s.location_name} [{s.location_key}] ({s.location_kind})")
    typer.echo("Bisogni:")
    for kind in NeedKind:
        v = s.needs.get(kind)
        if v is None:
            typer.echo(f"  {kind.value}: (mancante)")
        else:
            typer.echo(f"  {kind.value}: {v:.1f}")
    if s.relationships:
        typer.echo("Relazioni:")
        for k, v in s.relationships.items():
            typer.echo(f"  → {k}: {v:.1f}")
    else:
        typer.echo("Relazioni: nessuna")
    typer.echo(f"Azioni disponibili qui: {', '.join(s.available_actions) or 'nessuna'}")
    if s.unnecessary_actions:
        typer.echo(f"Non necessarie (bisogno già alto): {', '.join(s.unnecessary_actions)}")
    if s.other_characters_here:
        typer.echo(f"Presenti qui: {', '.join(s.other_characters_here)}")
    else:
        typer.echo("Presenti qui: nessuno")
    typer.echo("Location:")
    for loc in s.available_locations:
        marker = "←" if loc["key"] == s.location_key else " "
        typer.echo(f"  {marker} [{loc['key']}] {loc['name']}")


@player_app.command("do")
def do(
    action: ActionKind = typer.Option(..., "--action", "-a"),
) -> None:
    """Esegue un'azione del player nella location corrente.

    Non avanza il tempo: il tempo avanza con `simai sim tick`.
    """
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        s = build_player_status(session)
        if s is None:
            typer.echo("Nessun player nel mondo.", err=True)
            raise typer.Exit(code=1)
        result = do_action(session, s.character_key, action)
        if not result.success:
            session.rollback()
            typer.echo(f"Errore: {result.error}", err=True)
            raise typer.Exit(code=1)
        session.commit()

    typer.echo(f"{result.character_key} esegue {result.action.value} in [{result.location_key}]")
    if (
        result.need_kind is not None
        and result.need_before is not None
        and result.need_after is not None
    ):
        typer.echo(
            f"  {result.need_kind.value}: {result.need_before:.1f} → {result.need_after:.1f}"
        )
    if result.relationship_strength_after is not None:
        typer.echo(f"  relazione: {result.relationship_strength_after:.1f}")


@player_app.command("move")
def move(
    location: str = typer.Option(..., "--location", "-l"),
) -> None:
    """Sposta il player in un'altra location (istantaneo in 1.0)."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        s = build_player_status(session)
        if s is None:
            typer.echo("Nessun player nel mondo.", err=True)
            raise typer.Exit(code=1)
        result = move_character(session, s.character_key, location)
        if not result.success:
            session.rollback()
            typer.echo(f"Errore: {result.error}", err=True)
            raise typer.Exit(code=1)
        session.commit()

    typer.echo(f"{result.character_key}: {result.from_location_key} → {result.to_location_key}")
