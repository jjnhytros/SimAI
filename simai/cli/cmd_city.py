"""Comandi `city`: servizi, bilancio, tasse, soddisfazione."""

from __future__ import annotations

import typer
from rich.table import Table

from simai.city import (
    CityService,
    PublicServiceType,
    SatisfactionService,
    TaxService,
)
from simai.city.infrastructure import (
    LIGHT_COSTS,
    LIGHT_RADII,
    ROAD_COSTS,
    InfrastructureService,
    LightType,
    RoadType,
    road_condition_from_value,
)
from simai.city.mood import CityMoodService
from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.db.session import get_session_factory
from simai.npc.models import Character
from simai.npc.mood import MoodState

city_app = typer.Typer(
    name="city",
    help="Servizi pubblici, bilancio, tasse, soddisfazione.",
    no_args_is_help=True,
)


def _require_migrated() -> None:
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# services
# ---------------------------------------------------------------------------


@city_app.command("services")
def city_services() -> None:
    """Elenca i servizi pubblici attivi."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        services = CityService.all_services(session)
        rows: list[tuple[int, int, str, float, int, int, bool]] = [
            (
                s.id,
                s.district_id,
                s.type,
                s.quality,
                s.daily_cost,
                s.coverage_radius,
                s.is_active,
            )
            for s in services
        ]

    if not rows:
        console.print("[yellow]Nessun servizio pubblico.[/]")
        return

    table = Table(title=f"Servizi pubblici ({len(rows)})")
    table.add_column("ID", style="cyan")
    table.add_column("Distr.", justify="right")
    table.add_column("Tipo", style="magenta")
    table.add_column("Qualità", justify="right")
    table.add_column("Costo/g", justify="right")
    table.add_column("Raggio", justify="right")
    table.add_column("Attivo", justify="center")
    for sid, did, t, q, cost, radius, active in rows:
        color = "green" if q >= 0.75 else ("yellow" if q >= 0.40 else "red")
        table.add_row(
            str(sid),
            str(did),
            t,
            f"[{color}]{q:.2f}[/]",
            str(cost),
            str(radius),
            "✓" if active else "✗",
        )
    console.print(table)


@city_app.command("register-service")
def city_register_service(
    district_id: int = typer.Argument(...),
    type_: str = typer.Argument(..., help="POLICE, SCHOOL, HOSPITAL, FIRE, GARBAGE, PARK"),
    quality: float = typer.Option(0.6, "--quality", "-q", min=0.0, max=1.0),
    daily_cost: int | None = typer.Option(None, "--cost", "-c", min=0),
) -> None:
    """Registra un servizio pubblico."""
    _require_migrated()
    try:
        t = PublicServiceType(type_.upper())
    except ValueError:
        valid = ", ".join(x.value for x in PublicServiceType)
        console.print(f"[red]Tipo non valido. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        svc = CityService.register_service(
            session,
            district_id=district_id,
            type_=t,
            quality=quality,
            daily_cost=daily_cost,
        )
        session.commit()

    console.print(
        f"[green]Servizio registrato:[/] id={svc.id} {svc.type} "
        f"(q={svc.quality:.2f}, cost={svc.daily_cost})"
    )


# ---------------------------------------------------------------------------
# budget
# ---------------------------------------------------------------------------


@city_app.command("budget")
def city_budget() -> None:
    """Mostra il bilancio della città."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        b = CityService.get_budget(session)
        session.commit()

    table = Table(title="Bilancio città")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = "green" if b.balance > 0 else "red"
    table.add_row("balance", f"[{color}]{b.balance}[/]")
    table.add_row("total_revenue", str(b.total_revenue))
    table.add_row("total_expenses", str(b.total_expenses))
    table.add_row("net", f"{b.total_revenue - b.total_expenses:+d}")
    console.print(table)


@city_app.command("tick")
def city_tick() -> None:
    """Forza un tick giornaliero (paga i servizi)."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        report = CityService.daily_tick(session, current_dt=start)
        session.commit()

    table = Table(title="City tick")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("total_expense", str(report.total_expense))
    table.add_row("services_paid", str(report.services_paid))
    table.add_row("services_unpaid", str(report.services_unpaid))
    table.add_row("budget_balance", str(report.budget_balance))
    console.print(table)


# ---------------------------------------------------------------------------
# taxes
# ---------------------------------------------------------------------------


@city_app.command("taxes")
def city_taxes(
    character_id: int = typer.Argument(...),
) -> None:
    """Mostra le tasse pagate da un character."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        payments = TaxService.payments_of(session, character_id, limit=30)

    if not payments:
        console.print(f"[yellow]{c.full_name} non ha pagato tasse.[/]")
        return

    table = Table(title=f"Tasse di {c.full_name}")
    table.add_column("ID", style="cyan")
    table.add_column("Kind", style="magenta")
    table.add_column("Amount", justify="right")
    table.add_column("Tick", justify="right", style="dim")
    for p in payments:
        table.add_row(str(p.id), p.kind, str(p.amount), str(p.at_total_seconds))
    console.print(table)


# ---------------------------------------------------------------------------
# satisfaction
# ---------------------------------------------------------------------------


@city_app.command("satisfaction")
def city_satisfaction() -> None:
    """Mostra la soddisfazione dei cittadini per quartiere."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        report = SatisfactionService.compute_all(session)

    if not report.districts:
        console.print("[yellow]Nessun quartiere.[/]")
        return

    table = Table(title="Soddisfazione cittadini")
    table.add_column("Quartiere", style="cyan")
    table.add_column("Safety", justify="right")
    table.add_column("Health", justify="right")
    table.add_column("Edu", justify="right")
    table.add_column("Clean", justify="right")
    table.add_column("Well", justify="right")
    table.add_column("Overall", justify="right", style="green")

    def fmt(v: float) -> str:
        color = "green" if v >= 0.65 else ("yellow" if v >= 0.40 else "red")
        return f"[{color}]{v:.2f}[/]"

    for d in report.districts:
        table.add_row(
            d.district_name,
            fmt(d.safety),
            fmt(d.health),
            fmt(d.education),
            fmt(d.cleanliness),
            fmt(d.wellbeing),
            fmt(d.overall),
        )
    console.print(table)
    console.print(f"[bold]Overall città:[/] {report.overall:.3f}")


@city_app.command("citizens-mood")
def city_citizens_mood() -> None:
    """Mostra i moodlet città attivi sui cittadini."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        chars = list(session.query(Character).filter(Character.is_alive.is_(True)).all())
        rows: list[tuple[int, str, str, float, int]] = []
        for c in chars:
            mood = MoodState.from_dict(c.mood_json or {})
            for m in mood.moodlets:
                if m.source.startswith("city_"):
                    rows.append((c.id, c.full_name, m.name, m.happiness_delta, m.remaining_ticks))

    if not rows:
        console.print("[yellow]Nessun moodlet città attivo.[/]")
        return

    table = Table(title=f"Moodlet città attivi ({len(rows)})")
    table.add_column("ID", style="cyan")
    table.add_column("Character", style="magenta")
    table.add_column("Moodlet", style="yellow")
    table.add_column("Delta", justify="right")
    table.add_column("Tick", justify="right")
    for cid, name, moodlet, delta, remaining in rows:
        color = "green" if delta > 0 else "red"
        table.add_row(str(cid), name, moodlet, f"[{color}]{delta:+.2f}[/]", str(remaining))
    console.print(table)


@city_app.command("mood-tick")
def city_mood_tick() -> None:
    """Forza un tick di moodlet città (dev tool)."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        chars = list(session.query(Character).filter(Character.is_alive.is_(True)).all())
        report = CityMoodService.daily_tick(session, chars, current_dt=start)
        session.commit()

    table = Table(title="City mood tick")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("citizens_processed", str(report.citizens_processed))
    table.add_row("moodlets_applied", str(report.moodlets_applied))
    table.add_row("districts_evaluated", str(report.districts_evaluated))
    console.print(table)

    if report.district_overall:
        ov_table = Table(title="Overall per distretto")
        ov_table.add_column("District", style="cyan")
        ov_table.add_column("Overall", justify="right", style="magenta")
        for did, ov in sorted(report.district_overall.items()):
            ov_table.add_row(str(did), f"{ov:.3f}")
        console.print(ov_table)


# ---------------------------------------------------------------------------
# infrastructure
# ---------------------------------------------------------------------------


@city_app.command("infra-costs")
def city_infra_costs() -> None:
    """Mostra i costi di strade e lampioni."""
    table = Table(title="Costi infrastrutture")
    table.add_column("Tipo", style="cyan")
    table.add_column("Categoria", style="yellow")
    table.add_column("Costo", justify="right")
    table.add_column("Extra", style="dim")
    for road_t, road_cost in ROAD_COSTS.items():
        table.add_row(road_t.value, "strada", str(road_cost), "")
    for light_t, light_cost in LIGHT_COSTS.items():
        radius = LIGHT_RADII[light_t]
        table.add_row(light_t.value, "lampione", str(light_cost), f"radius={radius}")
    console.print(table)


@city_app.command("road-place")
def city_road_place(
    x: int = typer.Argument(..., help="Coordinata x."),
    y: int = typer.Argument(..., help="Coordinata y."),
    road_type: str = typer.Option("STREET", "--type", "-t"),
    buyer_id: int | None = typer.Option(None, "--buyer", "-b"),
) -> None:
    """Piazza una cella stradale."""
    _require_migrated()
    start = build_starting_datetime()
    try:
        rt = RoadType(road_type.upper())
    except ValueError:
        valid = ", ".join(x.value for x in RoadType)
        console.print(f"[red]Tipo non valido. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        buyer = session.get(Character, buyer_id) if buyer_id is not None else None
        result = InfrastructureService.place_road(
            session,
            x=x,
            y=y,
            road_type=rt,
            buyer=buyer,
            current_dt=start,
        )
        if result.ok:
            session.commit()

    if not result.ok:
        console.print(f"[red]Errore: {result.reason}[/]")
        raise typer.Exit(code=1)
    console.print(f"[green]Strada posata:[/] ({x},{y}) {rt.value} cost={result.cost_paid}")


@city_app.command("road-remove")
def city_road_remove(
    x: int = typer.Argument(...),
    y: int = typer.Argument(...),
) -> None:
    """Rimuove una cella stradale."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        ok = InfrastructureService.remove_road(session, x=x, y=y)
        session.commit()
    if not ok:
        console.print("[yellow]Nessuna strada in quella cella.[/]")
        return
    console.print(f"[green]Strada rimossa:[/] ({x},{y})")


@city_app.command("light-place")
def city_light_place(
    x: int = typer.Argument(...),
    y: int = typer.Argument(...),
    light_type: str = typer.Option("STANDARD", "--type", "-t"),
    buyer_id: int | None = typer.Option(None, "--buyer", "-b"),
) -> None:
    """Piazza un lampione."""
    _require_migrated()
    start = build_starting_datetime()
    try:
        lt = LightType(light_type.upper())
    except ValueError:
        valid = ", ".join(x.value for x in LightType)
        console.print(f"[red]Tipo non valido. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        buyer = session.get(Character, buyer_id) if buyer_id is not None else None
        result = InfrastructureService.place_light(
            session,
            x=x,
            y=y,
            light_type=lt,
            buyer=buyer,
            current_dt=start,
        )
        if result.ok:
            session.commit()

    if not result.ok:
        console.print(f"[red]Errore: {result.reason}[/]")
        raise typer.Exit(code=1)
    console.print(f"[green]Lampione posato:[/] ({x},{y}) {lt.value} cost={result.cost_paid}")


@city_app.command("light-remove")
def city_light_remove(
    x: int = typer.Argument(...),
    y: int = typer.Argument(...),
) -> None:
    """Rimuove un lampione."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        ok = InfrastructureService.remove_light(session, x=x, y=y)
        session.commit()
    if not ok:
        console.print("[yellow]Nessun lampione in quella cella.[/]")
        return
    console.print(f"[green]Lampione rimosso:[/] ({x},{y})")


@city_app.command("infra-list")
def city_infra_list(
    x0: int = typer.Option(0, "--x0", min=0, max=199),
    y0: int = typer.Option(0, "--y0", min=0, max=199),
    x1: int = typer.Option(50, "--x1", min=0, max=199),
    y1: int = typer.Option(50, "--y1", min=0, max=199),
) -> None:
    """Elenca strade e lampioni in un bounding box."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        roads = InfrastructureService.roads_in_bbox(session, x0=x0, y0=y0, x1=x1, y1=y1)
        lights = InfrastructureService.lights_in_bbox(session, x0=x0, y0=y0, x1=x1, y1=y1)

    rtable = Table(title=f"Strade ({len(roads)})")
    rtable.add_column("X", justify="right", style="cyan")
    rtable.add_column("Y", justify="right", style="cyan")
    rtable.add_column("Tipo", style="magenta")
    rtable.add_column("Cond", justify="right")
    rtable.add_column("Stato", style="yellow")
    for r in roads:
        cond = road_condition_from_value(r.condition)
        rtable.add_row(
            str(r.x),
            str(r.y),
            r.road_type,
            f"{r.condition:.3f}",
            cond.value,
        )
    console.print(rtable)

    ltable = Table(title=f"Lampioni ({len(lights)})")
    ltable.add_column("X", justify="right", style="cyan")
    ltable.add_column("Y", justify="right", style="cyan")
    ltable.add_column("Tipo", style="magenta")
    ltable.add_column("Raggio", justify="right")
    ltable.add_column("Cond", justify="right")
    ltable.add_column("Attivo", justify="center")
    for light in lights:
        ltable.add_row(
            str(light.x),
            str(light.y),
            light.light_type,
            str(light.radius),
            f"{light.condition:.3f}",
            "✓" if light.is_active else "✗",
        )
    console.print(ltable)


@city_app.command("infra-tick")
def city_infra_tick() -> None:
    """Forza un tick di degrado infrastrutture (dev tool)."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        report = InfrastructureService.daily_tick(session, current_dt=start)
        session.commit()

    table = Table(title="Infrastructure tick")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("roads_degraded", str(report.roads_degraded))
    table.add_row("lights_degraded", str(report.lights_degraded))
    table.add_row("lights_turned_off", str(report.lights_turned_off))
    console.print(table)


@city_app.command("coverage")
def city_coverage(
    x: int = typer.Argument(..., help="Coordinata x."),
    y: int = typer.Argument(..., help="Coordinata y."),
) -> None:
    """Mostra la copertura luminosa di una cella."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        cov = InfrastructureService.lighting_coverage_at(session, x=x, y=y)

    table = Table(title=f"Coverage @ ({x},{y})")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = "green" if cov >= 0.7 else ("yellow" if cov >= 0.3 else "red")
    table.add_row("lighting", f"[{color}]{cov:.3f}[/]")
    console.print(table)


def register(app: typer.Typer) -> None:
    """Registra il sub-app `city` sull'app root."""
    app.add_typer(city_app, name="city")
