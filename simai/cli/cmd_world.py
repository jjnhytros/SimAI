"""Comandi `world`: seed, esplorazione, pathfinding."""

from __future__ import annotations

import typer
from rich.table import Table
from sqlalchemy.exc import OperationalError

from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.db.session import get_session_factory
from simai.world import (
    DistrictType,
    LocationGraph,
    LotUsage,
    create_district,
    create_lot,
    district_summaries,
    get_location,
    list_locations,
    list_objects,
    list_objects_in,
    lot_summaries,
    seed_demo_world,
)
from simai.world.build import BuildService, WallOrientation
from simai.world.buy import (
    BuyService,
    ObjectCategory,
)
from simai.world.lot_service import get_lot
from simai.world.style import StyleKind, StyleService, WallSide
from simai.world.terrain import TerrainService, TerrainType

world_app = typer.Typer(
    name="world",
    help="Mondo: location, oggetti, navigazione.",
    no_args_is_help=True,
)


@world_app.command("seed")
def world_seed() -> None:
    """Popola il DB con un mondo demo (idempotente)."""
    if not check_migrations_applied():
        console.print(
            "[yellow]Database non migrato o tabella alembic_version assente.[/]\n"
            "[yellow]Esegui prima:[/] [bold]uv run python -m simai db upgrade[/]"
        )
        raise typer.Exit(code=1)

    factory = get_session_factory()
    try:
        with factory() as session:
            result = seed_demo_world(session)
            session.commit()
    except OperationalError as exc:
        console.print(
            f"[red]Errore DB: {exc.orig if hasattr(exc, 'orig') else exc}[/]\n"
            "[yellow]Suggerimento:[/] [bold]uv run python -m simai db upgrade[/]"
        )
        raise typer.Exit(code=1) from exc

    if result.locations_created == 0:
        console.print("[yellow]Mondo già popolato — nessuna azione.[/]")
    else:
        console.print(
            f"[green]Seed completato:[/] "
            f"locations={result.locations_created} "
            f"edges={result.edges_created} "
            f"objects={result.objects_created}"
        )


@world_app.command("list")
def world_list() -> None:
    """Elenca tutte le Location."""
    factory = get_session_factory()
    with factory() as session:
        locations = list_locations(session)

    if not locations:
        console.print("[yellow]Nessuna location. Esegui prima `world seed`.[/]")
        return

    table = Table(title="SimAI — Location")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="green")
    table.add_column("Parent", justify="right")
    table.add_column("Cap", justify="right")
    table.add_column("Pulizia", justify="right")
    table.add_column("Rumore", justify="right")
    table.add_column("Bounds")
    for loc in locations:
        table.add_row(
            str(loc.id),
            loc.name,
            loc.type,
            str(loc.parent_id) if loc.parent_id else "—",
            str(loc.capacity),
            f"{loc.cleanliness_level:.2f}",
            f"{loc.noise_level:.2f}",
            f"{loc.bounds_x},{loc.bounds_y} {loc.bounds_w}x{loc.bounds_h}",
        )
    console.print(table)


@world_app.command("show")
def world_show(
    location_id: int = typer.Argument(..., help="ID della location."),
) -> None:
    """Mostra dettagli di una Location + oggetti contenuti."""
    factory = get_session_factory()
    with factory() as session:
        loc = get_location(session, location_id)
        if loc is None:
            console.print(f"[red]Location id={location_id} non trovata.[/]")
            raise typer.Exit(code=1)
        objs = list_objects_in(session, location_id)

    table = Table(title=f"Location #{loc.id} — {loc.name}")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("name", loc.name)
    table.add_row("type", loc.type)
    table.add_row("parent_id", str(loc.parent_id) if loc.parent_id else "—")
    table.add_row("lot_id", str(loc.lot_id) if loc.lot_id else "—")
    table.add_row("bounds", f"{loc.bounds_x},{loc.bounds_y} {loc.bounds_w}x{loc.bounds_h}")
    table.add_row("capacity", str(loc.capacity))
    table.add_row("cleanliness_level", f"{loc.cleanliness_level:.3f}")
    table.add_row("noise_level", f"{loc.noise_level:.3f}")
    table.add_row("crowd_level", str(loc.crowd_level))
    table.add_row("safety_rating", f"{loc.safety_rating:.3f}")
    table.add_row("aesthetic_score", f"{loc.aesthetic_score:.3f}")
    table.add_row("attributes", str(loc.attributes_json))
    console.print(table)

    if objs:
        ot = Table(title="Oggetti nella location")
        ot.add_column("ID", style="cyan", no_wrap=True)
        ot.add_column("Nome", style="magenta")
        ot.add_column("Tipo", style="green")
        ot.add_column("Stato", style="yellow")
        ot.add_column("Cond.", justify="right")
        ot.add_column("Interazioni")
        for o in objs:
            ot.add_row(
                str(o.id),
                o.name,
                o.type,
                o.state,
                f"{o.condition:.2f}",
                ",".join(o.interactions_json or []) or "—",
            )
        console.print(ot)
    else:
        console.print("[dim]Nessun oggetto in questa location.[/]")


@world_app.command("objects")
def world_objects(
    location_id: int | None = typer.Option(
        None, "--location", "-l", help="Filtra per location ID."
    ),
) -> None:
    """Elenca tutti gli oggetti (opzionalmente filtrati per location)."""
    factory = get_session_factory()
    with factory() as session:
        objs = (
            list_objects_in(session, location_id)
            if location_id is not None
            else list_objects(session)
        )

    if not objs:
        console.print("[yellow]Nessun oggetto. Esegui prima `world seed`.[/]")
        return

    table = Table(title="SimAI — Game Objects")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="green")
    table.add_column("Location", justify="right")
    table.add_column("Stato", style="yellow")
    table.add_column("Cond.", justify="right")
    table.add_column("Container", justify="right")
    for o in objs:
        cont = (
            f"{len(o.container_contents_json or [])}/{o.container_capacity}"
            if o.container_capacity is not None
            else "—"
        )
        table.add_row(
            str(o.id),
            o.name,
            o.type,
            str(o.location_id) if o.location_id else "—",
            o.state,
            f"{o.condition:.2f}",
            cont,
        )
    console.print(table)


@world_app.command("path")
def world_path(
    from_id: int = typer.Argument(..., help="ID location di partenza."),
    to_id: int = typer.Argument(..., help="ID location di arrivo."),
) -> None:
    """Calcola il percorso A* tra due location."""
    factory = get_session_factory()
    with factory() as session:
        graph = LocationGraph.from_session(session)
        from_loc = get_location(session, from_id)
        to_loc = get_location(session, to_id)

        if from_loc is None or to_loc is None:
            console.print("[red]Location di partenza o arrivo non trovata.[/]")
            raise typer.Exit(code=1)

        result = graph.find_path(from_id, to_id)
        names = {loc.id: loc.name for loc in list_locations(session)}

    if result is None:
        console.print(f"[red]Nessun percorso da {from_id} a {to_id}.[/]")
        raise typer.Exit(code=1)

    table = Table(title=f"Percorso {from_id} → {to_id}")
    table.add_column("Step", justify="right")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    for i, node in enumerate(result.nodes):
        table.add_row(str(i), str(node), names.get(node, "?"))
    console.print(table)
    console.print(
        f"[green]Distanza totale:[/] {result.total_distance:.3f} ({len(result.nodes)} nodi)"
    )


# ---------------------------------------------------------------------------
# districts
# ---------------------------------------------------------------------------


@world_app.command("districts")
def world_districts() -> None:
    """Elenca i quartieri."""
    factory = get_session_factory()
    with factory() as session:
        summaries = district_summaries(session)

    if not summaries:
        console.print("[yellow]Nessun quartiere. Esegui `world seed`.[/]")
        return

    table = Table(title="Quartieri")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="green")
    table.add_column("Bounds")
    table.add_column("Tasse", justify="right")
    table.add_column("Lotti", justify="right")
    for d in summaries:
        table.add_row(
            str(d.id),
            d.name,
            d.type,
            f"{d.bounds[0]},{d.bounds[1]} {d.bounds[2]}x{d.bounds[3]}",
            f"{d.tax_rate:.2%}",
            str(d.lot_count),
        )
    console.print(table)


@world_app.command("district-create")
def world_district_create(
    name: str = typer.Argument(..., help="Nome del quartiere."),
    type_: str = typer.Option(
        "MIXED", "--type", "-t", help="RESIDENTIAL/COMMERCIAL/INDUSTRIAL/MIXED/RURAL."
    ),
    bounds: str = typer.Option("0,0,50,50", "--bounds", "-b"),
    tax_rate: float = typer.Option(0.05, "--tax", min=0.0, max=1.0),
) -> None:
    """Crea un nuovo quartiere."""
    try:
        dtype = DistrictType(type_.upper())
    except ValueError:
        valid = ", ".join(x.value for x in DistrictType)
        console.print(f"[red]Tipo sconosciuto. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    try:
        x, y, w, h = (int(v) for v in bounds.split(","))
    except ValueError:
        console.print("[red]Bounds non validi (atteso x,y,w,h).[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        d = create_district(
            session,
            name=name,
            type_=dtype,
            bounds=(x, y, w, h),
            tax_rate=tax_rate,
        )
        session.commit()

    console.print(f"[green]Quartiere creato:[/] id={d.id} name={d.name!r} type={d.type}")


# ---------------------------------------------------------------------------
# lots
# ---------------------------------------------------------------------------


@world_app.command("lots")
def world_lots(
    district_id: int | None = typer.Option(None, "--district", "-d", help="Filtra per quartiere."),
) -> None:
    """Elenca i lotti."""
    factory = get_session_factory()
    with factory() as session:
        summaries = lot_summaries(session, district_id=district_id)

    if not summaries:
        console.print("[yellow]Nessun lotto.[/]")
        return

    table = Table(title="Lotti")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Distr.", justify="right")
    table.add_column("Uso", style="green")
    table.add_column("Bounds")
    table.add_column("Prezzo", justify="right")
    table.add_column("Dev", justify="center")
    for lot in summaries:
        table.add_row(
            str(lot.id),
            lot.name,
            str(lot.district_id),
            lot.usage,
            f"{lot.bounds[0]},{lot.bounds[1]} {lot.bounds[2]}x{lot.bounds[3]}",
            str(lot.base_price),
            "✓" if lot.is_developed else "",
        )
    console.print(table)


@world_app.command("lot-create")
def world_lot_create(
    district_id: int = typer.Argument(..., help="ID del quartiere."),
    name: str = typer.Argument(..., help="Nome del lotto."),
    usage: str = typer.Option(
        "VACANT",
        "--usage",
        "-u",
        help="RESIDENTIAL/COMMERCIAL/INDUSTRIAL/PUBLIC/VACANT/PARK.",
    ),
    bounds: str = typer.Option("0,0,10,10", "--bounds", "-b"),
    base_price: int = typer.Option(1000, "--price", "-p", min=0),
) -> None:
    """Crea un nuovo lotto."""
    try:
        u = LotUsage(usage.upper())
    except ValueError:
        valid = ", ".join(x.value for x in LotUsage)
        console.print(f"[red]Uso sconosciuto. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    try:
        x, y, w, h = (int(v) for v in bounds.split(","))
    except ValueError:
        console.print("[red]Bounds non validi (atteso x,y,w,h).[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    try:
        with factory() as session:
            lot = create_lot(
                session,
                district_id=district_id,
                name=name,
                usage=u,
                bounds=(x, y, w, h),
                base_price=base_price,
            )
            session.commit()
    except LookupError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Lotto creato:[/] id={lot.id} name={lot.name!r} "
        f"usage={lot.usage} price={lot.base_price}"
    )


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


@world_app.command("build-show")
def world_build_show(
    lot_id: int = typer.Argument(..., help="ID del lotto."),
) -> None:
    """Mostra il layout di build (muri, aperture, stanze)."""
    factory = get_session_factory()
    with factory() as session:
        lot = get_lot(session, lot_id)
        if lot is None:
            console.print(f"[red]Lot id={lot_id} non trovato.[/]")
            raise typer.Exit(code=1)
        layout = BuildService.layout_of(session, lot)

    console.print(f"[bold]Lot {lot.id}:[/] {lot.name} ({layout.grid_w}x{layout.grid_h})")

    wall_table = Table(title=f"Muri ({len(layout.walls)})")
    wall_table.add_column("ID", style="cyan")
    wall_table.add_column("Pos")
    wall_table.add_column("Orient")
    wall_table.add_column("Material")
    for w in layout.walls:
        wall_table.add_row(
            str(w["id"]),
            f"({w['x']},{w['y']})",
            str(w["orientation"]),
            str(w["material"]),
        )
    console.print(wall_table)

    op_table = Table(title=f"Aperture ({len(layout.openings)})")
    op_table.add_column("ID", style="cyan")
    op_table.add_column("Wall", justify="right")
    op_table.add_column("Tipo", style="yellow")
    for o in layout.openings:
        op_table.add_row(str(o["id"]), str(o["wall_id"]), str(o["kind"]))
    console.print(op_table)

    room_table = Table(title=f"Stanze rilevate ({len(layout.rooms)})")
    room_table.add_column("Bounds")
    room_table.add_column("Area", justify="right")
    for r in layout.rooms:
        room_table.add_row(
            f"({r['x']},{r['y']}) {r['w']}x{r['h']}",
            str(r["area"]),
        )
    console.print(room_table)


@world_app.command("build-wall")
def world_build_wall(
    lot_id: int = typer.Argument(..., help="ID del lotto."),
    x: int = typer.Argument(..., help="Coordinata x."),
    y: int = typer.Argument(..., help="Coordinata y."),
    orientation: str = typer.Option(
        "H", "--orientation", "-o", help="H (orizzontale) o V (verticale)."
    ),
) -> None:
    """Aggiunge un muro."""
    try:
        o = WallOrientation(orientation.upper())
    except ValueError:
        console.print("[red]Orientation deve essere H o V.[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        lot = get_lot(session, lot_id)
        if lot is None:
            console.print(f"[red]Lot id={lot_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            wall = BuildService.add_wall(session, lot=lot, x=x, y=y, orientation=o)
        except Exception as exc:
            console.print(f"[red]Errore: {exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
    console.print(f"[green]Muro aggiunto:[/] id={wall.id} ({wall.x},{wall.y}) {wall.orientation}")


@world_app.command("build-clear")
def world_build_clear(
    lot_id: int = typer.Argument(..., help="ID del lotto."),
) -> None:
    """Rimuove tutti i muri e le aperture di un lotto."""
    factory = get_session_factory()
    with factory() as session:
        n = BuildService.clear_walls(session, lot_id)
        session.commit()
    console.print(f"[green]Rimossi {n} muri dal lotto {lot_id}.[/]")


# ---------------------------------------------------------------------------
# catalog / place-object / objects-on-lot
# ---------------------------------------------------------------------------


@world_app.command("catalog")
def world_catalog(
    category: str | None = typer.Option(None, "--category", "-c", help="Filtra per categoria."),
) -> None:
    """Elenca il catalogo oggetti."""
    cat: ObjectCategory | None = None
    if category is not None:
        try:
            cat = ObjectCategory(category.upper())
        except ValueError:
            valid = ", ".join(x.value for x in ObjectCategory)
            console.print(f"[red]Categoria non valida. Valide: {valid}[/]")
            raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        items = BuyService.list_catalog(session, category=cat)

    if not items:
        console.print("[yellow]Catalogo vuoto. Esegui `world seed`.[/]")
        return

    table = Table(title=f"Catalogo oggetti ({len(items)})")
    table.add_column("ID", style="cyan")
    table.add_column("Code", style="dim")
    table.add_column("Nome", style="magenta")
    table.add_column("Categoria", style="green")
    table.add_column("Prezzo", justify="right")
    table.add_column("Footprint", justify="center")
    table.add_column("Container", justify="center")
    for it in items:
        table.add_row(
            str(it.id),
            it.type_code,
            it.name,
            it.category,
            str(it.base_price),
            f"{it.footprint_w}x{it.footprint_h}",
            "✓" if it.is_container else "",
        )
    console.print(table)


@world_app.command("place-object")
def world_place_object(
    lot_id: int = typer.Argument(..., help="ID del lotto."),
    catalog_id: int = typer.Argument(..., help="ID voce di catalogo."),
    x: int = typer.Argument(..., help="Coordinata x (lot-local)."),
    y: int = typer.Argument(..., help="Coordinata y (lot-local)."),
    rotation: int = typer.Option(0, "--rotation", "-r", help="0/90/180/270."),
    buyer_id: int | None = typer.Option(
        None, "--buyer", "-b", help="ID del compratore (paga l'oggetto)."
    ),
    supplier_id: int | None = typer.Option(
        None, "--supplier", "-s", help="ID del fornitore (default: più economico con stock)."
    ),
) -> None:
    """Piazza un oggetto dal catalogo su un lotto.

    Con `--buyer`, i soldi vengono scalati dal bilancio del buyer e lo
    stock dal fornitore. Senza, piazzamento sandbox gratuito.
    """
    from simai.npc.models import Character as _Char

    factory = get_session_factory()
    start = build_starting_datetime()
    with factory() as session:
        lot = get_lot(session, lot_id)
        if lot is None:
            console.print(f"[red]Lot id={lot_id} non trovato.[/]")
            raise typer.Exit(code=1)
        catalog = BuyService.catalog_by_id(session, catalog_id)
        if catalog is None:
            console.print(f"[red]Catalog id={catalog_id} non trovato.[/]")
            raise typer.Exit(code=1)

        buyer = None
        if buyer_id is not None:
            buyer = session.get(_Char, buyer_id)
            if buyer is None:
                console.print(f"[red]Buyer id={buyer_id} non trovato.[/]")
                raise typer.Exit(code=1)

        result = BuyService.place_object(
            session,
            lot=lot,
            catalog=catalog,
            x=x,
            y=y,
            rotation=rotation,
            buyer=buyer,
            supplier_location_id=supplier_id,
            current_dt=start,
        )
        if result.ok:
            session.commit()

    if not result.ok:
        console.print(f"[red]Piazzamento fallito: {result.reason}[/]")
        raise typer.Exit(code=1)

    table = Table(title="Oggetto piazzato")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("object_id", str(result.object_id))
    table.add_row("catalog", f"{catalog.type_code} ({catalog.name})")
    table.add_row("position", f"({x},{y}) rot={rotation}")
    table.add_row("cost_paid", str(result.cost_paid))
    table.add_row(
        "supplier",
        str(result.supplier_location_id) if result.supplier_location_id else "—",
    )
    console.print(table)


@world_app.command("objects-on-lot")
def world_objects_on_lot(
    lot_id: int = typer.Argument(..., help="ID del lotto."),
) -> None:
    """Elenca gli oggetti piazzati su un lotto."""
    factory = get_session_factory()
    with factory() as session:
        objects = BuyService.objects_on_lot(session, lot_id)

    if not objects:
        console.print("[yellow]Nessun oggetto piazzato.[/]")
        return

    table = Table(title=f"Oggetti sul lotto {lot_id} ({len(objects)})")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="green")
    table.add_column("Pos", justify="right")
    table.add_column("Rot", justify="right")
    table.add_column("Stato", style="yellow")
    for o in objects:
        table.add_row(
            str(o.id),
            o.name,
            o.type,
            f"({o.position_x},{o.position_y})",
            f"{o.rotation}°",
            o.state,
        )
    console.print(table)


# ---------------------------------------------------------------------------
# styles / set-floor / set-wall-style
# ---------------------------------------------------------------------------


@world_app.command("styles")
def world_styles(
    kind: str | None = typer.Option(None, "--kind", "-k", help="FLOOR o WALL."),
) -> None:
    """Elenca il catalogo stili."""
    k: StyleKind | None = None
    if kind is not None:
        try:
            k = StyleKind(kind.upper())
        except ValueError:
            console.print("[red]Kind deve essere FLOOR o WALL.[/]")
            raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        items = StyleService.list_catalog(session, kind=k)

    if not items:
        console.print("[yellow]Catalogo stili vuoto. Esegui `world seed`.[/]")
        return

    table = Table(title=f"Stili ({len(items)})")
    table.add_column("ID", style="cyan")
    table.add_column("Code", style="dim")
    table.add_column("Nome", style="magenta")
    table.add_column("Kind", style="green")
    table.add_column("Colore", style="yellow")
    table.add_column("Prezzo", justify="right")
    table.add_column("Pattern")
    for it in items:
        table.add_row(
            str(it.id),
            it.type_code,
            it.name,
            it.kind,
            it.color_hex,
            str(it.base_price),
            it.pattern,
        )
    console.print(table)


@world_app.command("set-floor")
def world_set_floor(
    lot_id: int = typer.Argument(...),
    style_id: int = typer.Argument(...),
    x: int = typer.Argument(...),
    y: int = typer.Argument(...),
    buyer_id: int | None = typer.Option(None, "--buyer", "-b"),
) -> None:
    """Applica uno stile pavimento a una cella."""
    from simai.npc.models import Character as _Char

    factory = get_session_factory()
    with factory() as session:
        lot = get_lot(session, lot_id)
        style = StyleService.by_id(session, style_id)
        if lot is None or style is None:
            console.print("[red]Lot o style non trovati.[/]")
            raise typer.Exit(code=1)
        buyer = session.get(_Char, buyer_id) if buyer_id is not None else None
        result = StyleService.set_floor(session, lot=lot, x=x, y=y, style=style, buyer=buyer)
        if result.ok:
            session.commit()
    if not result.ok:
        console.print(f"[red]Errore: {result.reason}[/]")
        raise typer.Exit(code=1)
    console.print(f"[green]Pavimento applicato:[/] cost={result.cost_paid}")


@world_app.command("set-wall-style")
def world_set_wall_style(
    wall_id: int = typer.Argument(...),
    style_id: int = typer.Argument(...),
    buyer_id: int | None = typer.Option(None, "--buyer", "-b"),
) -> None:
    """Applica uno stile a un muro."""
    from simai.npc.models import Character as _Char
    from simai.world.build.models import Wall as _Wall

    factory = get_session_factory()
    with factory() as session:
        wall = session.get(_Wall, wall_id)
        style = StyleService.by_id(session, style_id)
        if wall is None or style is None:
            console.print("[red]Wall o style non trovati.[/]")
            raise typer.Exit(code=1)
        buyer = session.get(_Char, buyer_id) if buyer_id is not None else None
        result = StyleService.set_wall_style(
            session,
            wall=wall,
            style=style,
            side=WallSide.INTERIOR,
            buyer=buyer,
        )
        if result.ok:
            session.commit()
    if not result.ok:
        console.print(f"[red]Errore: {result.reason}[/]")
        raise typer.Exit(code=1)
    console.print(f"[green]Rivestimento applicato:[/] cost={result.cost_paid}")


# ---------------------------------------------------------------------------
# terrain
# ---------------------------------------------------------------------------


@world_app.command("terrain-types")
def world_terrain_types() -> None:
    """Elenca i tipi di terreno disponibili."""
    from simai.world.terrain import TERRAIN_COLORS, TERRAIN_LABELS

    table = Table(title="Tipi di terreno")
    table.add_column("Tipo", style="cyan")
    table.add_column("Etichetta", style="magenta")
    table.add_column("Colore", style="green")
    for t in TerrainType:
        table.add_row(t.value, TERRAIN_LABELS.get(t, t.value), TERRAIN_COLORS.get(t, "—"))
    console.print(table)


@world_app.command("set-terrain")
def world_set_terrain(
    lot_id: int = typer.Argument(...),
    terrain_type: str = typer.Argument(...),
    x: int = typer.Argument(...),
    y: int = typer.Argument(...),
    elevation: int = typer.Option(0, "--elev", "-e", min=0, max=3),
    buyer_id: int | None = typer.Option(None, "--buyer", "-b"),
) -> None:
    """Applica un tipo di terreno a una cella."""
    from simai.npc.models import Character as _Char

    try:
        t = TerrainType(terrain_type.upper())
    except ValueError:
        valid = ", ".join(x.value for x in TerrainType)
        console.print(f"[red]Tipo non valido. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        lot = get_lot(session, lot_id)
        if lot is None:
            console.print(f"[red]Lot id={lot_id} non trovato.[/]")
            raise typer.Exit(code=1)
        buyer = session.get(_Char, buyer_id) if buyer_id is not None else None
        result = TerrainService.set_terrain(
            session,
            lot=lot,
            x=x,
            y=y,
            terrain_type=t,
            elevation=elevation,
            buyer=buyer,
        )
        if result.ok:
            session.commit()

    if not result.ok:
        console.print(f"[red]Errore: {result.reason}[/]")
        raise typer.Exit(code=1)
    console.print(
        f"[green]Terreno applicato:[/] {t.value} @ ({x},{y}) elev={elevation} "
        f"cost={result.cost_paid}"
    )


@world_app.command("terrain-show")
def world_terrain_show(
    lot_id: int = typer.Argument(...),
) -> None:
    """Mostra i terrain tile di un lotto."""
    factory = get_session_factory()
    with factory() as session:
        tiles = TerrainService.tiles_of(session, lot_id)

    if not tiles:
        console.print("[yellow]Nessun terreno applicato.[/]")
        return

    table = Table(title=f"Terreno del lotto {lot_id} ({len(tiles)} celle)")
    table.add_column("X", justify="right", style="cyan")
    table.add_column("Y", justify="right", style="cyan")
    table.add_column("Tipo", style="green")
    table.add_column("Elev", justify="right")
    for t in tiles:
        table.add_row(str(t.x), str(t.y), t.terrain_type, str(t.elevation))
    console.print(table)


def register(app: typer.Typer) -> None:
    """Registra il sub-app `world` sull'app root."""
    app.add_typer(world_app, name="world")
