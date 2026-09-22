"""Comandi `transport`: veicoli, linee, viaggi."""

from __future__ import annotations

import typer
from rich.table import Table

from simai.city.transport import (
    MultiLegPlan,
    MultiLegPlanner,
    TransitService,
    TransportService,
    VehicleType,
)
from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.db.session import get_session_factory
from simai.npc.models import Character
from simai.world.models import Location

transport_app = typer.Typer(
    name="transport",
    help="Veicoli, linee, pathfinding multi-modale.",
    no_args_is_help=True,
)


def _require_migrated() -> None:
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)


@transport_app.command("vehicles")
def transport_vehicles(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Elenca i veicoli di un character."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        vehicles = TransportService.vehicles_of(session, character_id)

    if not vehicles:
        console.print(f"[yellow]{c.full_name} non ha veicoli.[/]")
        return

    table = Table(title=f"Veicoli di {c.full_name}")
    table.add_column("ID", style="cyan")
    table.add_column("Tipo", style="magenta")
    table.add_column("Fuel", justify="right")
    table.add_column("Cond", justify="right")
    table.add_column("Location", justify="right")
    for v in vehicles:
        table.add_row(
            str(v.id),
            v.vehicle_type,
            f"{v.fuel:.1f}",
            f"{v.condition:.2f}",
            str(v.location_id) if v.location_id else "—",
        )
    console.print(table)


@transport_app.command("buy-vehicle")
def transport_buy_vehicle(
    character_id: int = typer.Argument(...),
    vehicle_type: str = typer.Argument(..., help="CAR o BIKE."),
) -> None:
    """Acquista un veicolo."""
    _require_migrated()
    start = build_starting_datetime()
    try:
        vt = VehicleType(vehicle_type.upper())
    except ValueError:
        console.print("[red]Tipo: CAR o BIKE.[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        result = TransportService.buy_vehicle(
            session, character=c, vehicle_type=vt, current_dt=start
        )
        if result.ok:
            session.commit()

    if not result.ok:
        console.print(f"[red]Errore: {result.reason}[/]")
        raise typer.Exit(code=1)
    console.print(
        f"[green]Veicolo acquistato:[/] id={result.vehicle_id} "
        f"tipo={vt.value} costo={result.cost_paid}"
    )


@transport_app.command("refuel")
def transport_refuel(
    vehicle_id: int = typer.Argument(...),
) -> None:
    """Rifornisce un veicolo."""
    _require_migrated()
    from simai.city.transport.models import Vehicle

    factory = get_session_factory()
    with factory() as session:
        v = session.get(Vehicle, vehicle_id)
        if v is None:
            console.print(f"[red]Veicolo id={vehicle_id} non trovato.[/]")
            raise typer.Exit(code=1)
        new_fuel = TransportService.refuel_car(session, vehicle=v)
        session.commit()

    console.print(f"[green]Rifornito:[/] fuel={new_fuel:.1f}")


@transport_app.command("routes")
def transport_routes() -> None:
    """Elenca le linee attive."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        routes = TransportService.all_routes(session)
        rows: list[tuple[int, str, str, int, int, float]] = [
            (
                r.id,
                r.name,
                r.route_type,
                r.base_fare,
                len(TransportService.stops_of(session, r.id)),
                r.speed_cells_per_tick,
            )
            for r in routes
        ]

    if not rows:
        console.print("[yellow]Nessuna linea.[/]")
        return

    table = Table(title=f"Linee ({len(rows)})")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="green")
    table.add_column("Fare", justify="right")
    table.add_column("Fermate", justify="right")
    table.add_column("Speed", justify="right")
    for rid, name, rt, fare, stops, speed in rows:
        table.add_row(str(rid), name, rt, str(fare), str(stops), f"{speed:.1f}")
    console.print(table)


@transport_app.command("route-stops")
def transport_route_stops(
    route_id: int = typer.Argument(...),
) -> None:
    """Elenca le fermate di una linea."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        stops = TransportService.stops_of(session, route_id)
        rows: list[tuple[int, int, str]] = []
        for s in stops:
            loc = session.get(Location, s.location_id)
            rows.append((s.sequence, s.location_id, loc.name if loc else "?"))

    if not rows:
        console.print("[yellow]Nessuna fermata.[/]")
        return

    table = Table(title=f"Fermate linea {route_id}")
    table.add_column("Seq", justify="right", style="cyan")
    table.add_column("Loc ID", justify="right")
    table.add_column("Nome", style="magenta")
    for seq, loc_id, name in rows:
        table.add_row(str(seq), str(loc_id), name)
    console.print(table)


@transport_app.command("plan")
def transport_plan(
    character_id: int = typer.Argument(...),
    from_location: int = typer.Argument(...),
    to_location: int = typer.Argument(...),
) -> None:
    """Mostra il piano di viaggio tra due location."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        plans = TransportService.plan_all(
            session,
            c,
            from_location_id=from_location,
            to_location_id=to_location,
        )

    if not plans:
        console.print("[yellow]Nessun piano disponibile.[/]")
        return

    table = Table(title="Piani di viaggio")
    table.add_column("Modo", style="cyan")
    table.add_column("Distanza", justify="right")
    table.add_column("Tick", justify="right")
    table.add_column("Costo", justify="right")
    table.add_column("Fuel", justify="right")
    table.add_column("Descrizione", style="magenta")
    plans.sort(key=lambda p: (p.duration_ticks, p.cost))
    for p in plans:
        table.add_row(
            p.mode.value,
            f"{p.distance:.1f}",
            str(p.duration_ticks),
            str(p.cost),
            f"{p.fuel_needed:.1f}" if p.fuel_needed else "—",
            p.description,
        )
    console.print(table)


@transport_app.command("travel")
def transport_travel(
    character_id: int = typer.Argument(...),
    to_location: int = typer.Argument(...),
    instant: bool = typer.Option(False, "--instant", help="Teletrasporto immediato (dev tool)."),
) -> None:
    """Avvia un viaggio: in modalità transito temporale (default) o istantaneo."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        if c.location_id is None:
            console.print("[red]Character senza location di partenza.[/]")
            raise typer.Exit(code=1)
        plan = TransportService.plan(
            session,
            c,
            from_location_id=c.location_id,
            to_location_id=to_location,
        )
        if plan is None:
            console.print("[red]Nessun piano disponibile.[/]")
            raise typer.Exit(code=1)

        if instant:
            result = TransportService.travel(session, character=c, plan=plan, current_dt=start)
            if result.ok:
                session.commit()
            if not result.ok:
                console.print(f"[red]Errore: {result.reason}[/]")
                raise typer.Exit(code=1)
            console.print(
                f"[green]Viaggio istantaneo:[/] {plan.mode.value} "
                f"({plan.duration_ticks} tick, {result.cost_paid} Athel)"
            )
            return

        # Modalità transito
        try:
            job = TransitService.start(session, character=c, plan=plan, current_dt=start)
            session.commit()
        except ValueError as exc:
            console.print(f"[red]Errore: {exc}[/]")
            raise typer.Exit(code=1) from exc

        console.print(
            f"[green]Transito avviato:[/] job={job.id} {plan.mode.value} "
            f"→ loc={to_location} (arrivo a tick +{plan.duration_ticks})"
        )


@transport_app.command("transit-list")
def transport_transit_list() -> None:
    """Elenca tutti i transiti attivi."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        jobs = TransitService.all_active(session)
        rows: list[tuple[int, int, str, int, int, int]] = [
            (
                j.id,
                j.character_id,
                j.mode,
                j.from_location_id,
                j.to_location_id,
                j.arrives_at_total_seconds,
            )
            for j in jobs
        ]

    if not rows:
        console.print("[yellow]Nessun transito attivo.[/]")
        return

    table = Table(title=f"Transiti attivi ({len(rows)})")
    table.add_column("Job", style="cyan")
    table.add_column("Char", justify="right")
    table.add_column("Modo", style="magenta")
    table.add_column("From", justify="right")
    table.add_column("To", justify="right")
    table.add_column("Arriva (sec)", justify="right")
    for jid, cid, mode, frm, to, arrives in rows:
        table.add_row(str(jid), str(cid), mode, str(frm), str(to), str(arrives))
    console.print(table)


@transport_app.command("transit-status")
def transport_transit_status(
    character_id: int = typer.Argument(...),
) -> None:
    """Stato di transito di un character."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        job = TransitService.active_job(session, character_id)

    table = Table(title=f"Transito char {character_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    if job is None:
        table.add_row("status", "IDLE (nessun transito)")
    else:
        table.add_row("job_id", str(job.id))
        table.add_row("mode", job.mode)
        table.add_row("from_loc", str(job.from_location_id))
        table.add_row("to_loc", str(job.to_location_id))
        table.add_row("arrives_at", str(job.arrives_at_total_seconds))
        table.add_row("status", job.status)
    console.print(table)


@transport_app.command("plan-multi")
def transport_plan_multi(
    character_id: int = typer.Argument(...),
    from_location: int = typer.Argument(...),
    to_location: int = typer.Argument(...),
    limit: int = typer.Option(10, "--limit", "-l", min=1, max=30),
) -> None:
    """Mostra i piani multi-tratta (walk + bus/metro + walk, ecc.)."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        plans = MultiLegPlanner.plan_all(
            session,
            c,
            from_location_id=from_location,
            to_location_id=to_location,
        )

    if not plans:
        console.print("[yellow]Nessun piano multi-leg.[/]")
        return

    table = Table(title=f"Piani multi-tratta (top {limit})")
    table.add_column("Modalità", style="cyan")
    table.add_column("Tick", justify="right")
    table.add_column("Costo", justify="right")
    table.add_column("Fuel", justify="right")
    table.add_column("Descrizione", style="magenta")
    for p in plans[:limit]:
        table.add_row(
            p.mode_label,
            str(p.total_ticks),
            str(p.total_cost),
            f"{p.total_fuel:.1f}" if p.total_fuel else "—",
            p.description,
        )
    console.print(table)


@transport_app.command("travel-multi")
def transport_travel_multi(
    character_id: int = typer.Argument(...),
    to_location: int = typer.Argument(...),
    mode_label: str = typer.Option(
        "",
        "--mode",
        "-m",
        help="Modalità preferita (es. 'WALK+BUS+WALK'). Vuoto = la più veloce.",
    ),
    instant: bool = typer.Option(False, "--instant"),
) -> None:
    """Avvia un viaggio multi-tratta."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        if c.location_id is None:
            console.print("[red]Character senza location di partenza.[/]")
            raise typer.Exit(code=1)

        plans = MultiLegPlanner.plan_all(
            session,
            c,
            from_location_id=c.location_id,
            to_location_id=to_location,
        )
        if not plans:
            console.print("[red]Nessun piano disponibile.[/]")
            raise typer.Exit(code=1)

        plan = plans[0]
        if mode_label:
            matching = [p for p in plans if p.mode_label == mode_label.upper()]
            if not matching:
                console.print(f"[red]Nessun piano con modalità {mode_label!r}.[/]")
                raise typer.Exit(code=1)
            plan = matching[0]

        if instant:
            # Teletrasporto: crea job con durata 0
            from simai.city.transport.multi_leg import TravelLeg

            zero_plan = MultiLegPlan(
                legs=(
                    TravelLeg(
                        mode=plan.legs[0].mode,
                        from_location_id=plan.from_location_id,
                        to_location_id=plan.to_location_id,
                        duration_ticks=0,
                        cost=plan.total_cost,
                        fuel_needed=plan.total_fuel,
                        description="viaggio istantaneo",
                    ),
                )
            )
            try:
                job = TransitService.start(session, character=c, plan=zero_plan, current_dt=start)
                # Forza arrivo immediato
                job.arrives_at_total_seconds = start.to_total_seconds()
                session.commit()
            except ValueError as exc:
                console.print(f"[red]Errore: {exc}[/]")
                raise typer.Exit(code=1) from exc
            console.print(f"[green]Viaggio istantaneo programmato:[/] job={job.id}")
            return

        try:
            job = TransitService.start(session, character=c, plan=plan, current_dt=start)
            session.commit()
        except ValueError as exc:
            console.print(f"[red]Errore: {exc}[/]")
            raise typer.Exit(code=1) from exc

        table = Table(title="Transito multi-leg avviato")
        table.add_column("Chiave", style="cyan")
        table.add_column("Valore", style="magenta")
        table.add_row("job_id", str(job.id))
        table.add_row("modalità", plan.mode_label)
        table.add_row("legs", str(len(plan.legs)))
        table.add_row("durata (tick)", str(plan.total_ticks))
        table.add_row("costo", str(plan.total_cost))
        table.add_row("fuel", f"{plan.total_fuel:.2f}")
        console.print(table)


def register(app: typer.Typer) -> None:
    """Registra il sub-app `transport` sull'app root."""
    app.add_typer(transport_app, name="transport")
