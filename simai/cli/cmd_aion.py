"""Comandi `economy aion`: piattaforma, listing, ordini, spedizioni, magazzino.

Registrati come sottocomando di `economy` (`simai economy aion ...`).
"""

from __future__ import annotations

import random

import typer
from rich.table import Table
from sqlalchemy import func, select

from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.config.settings import get_settings
from simai.db.session import get_session_factory
from simai.economy.aion import (
    AION_ESCROW_CODE,
    AION_REVENUE_CODE,
    AionBuyerType,
    AionError,
    AionInventoryItem,
    AionListing,
    AionListingStatus,
    AionOrder,
    AionOrderStatus,
    AionProductType,
    AionSellerType,
    AionService,
    AionShipment,
    AionWarehouse,
    seed_demo_aion,
)
from simai.economy.ledger import LedgerService
from simai.npc.models import Character

aion_app = typer.Typer(
    name="aion",
    help="Piattaforma e-commerce AION (multivendor).",
    no_args_is_help=True,
)


def _require_migrated() -> None:
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# platform
# ---------------------------------------------------------------------------


@aion_app.command("platform")
def aion_platform() -> None:
    """Stato della piattaforma AION: config, conti ledger, magazzino globale."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        AionService.ensure_platform(session)
        session.commit()

        platform = AionService.get_platform(session)
        if platform is None:
            console.print("[red]Piattaforma AION non disponibile.[/]")
            raise typer.Exit(code=1)

        warehouse = AionService.get_global_warehouse(session)

        revenue_acc = LedgerService.get_account(session, AION_REVENUE_CODE)
        escrow_acc = LedgerService.get_account(session, AION_ESCROW_CODE)
        revenue_bal = LedgerService.get_signed_balance(session, revenue_acc) if revenue_acc else 0
        # LIABILITY: il saldo contabile è il negativo del signed flow-based
        escrow_bal = -LedgerService.get_signed_balance(session, escrow_acc) if escrow_acc else 0

        n_listings = int(
            session.scalar(
                select(func.count(AionListing.id)).where(
                    AionListing.status == AionListingStatus.ACTIVE.value
                )
            )
            or 0
        )
        n_orders = int(session.scalar(select(func.count(AionOrder.id))) or 0)

    table = Table(title=f"AION Platform — {platform.name} ({platform.code})")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("active", "✓" if platform.is_active else "✗")
    table.add_row("default_commission_rate", f"{platform.default_commission_rate:.2%}")
    table.add_row("default_fulfillment_mode", platform.default_fulfillment_mode)
    table.add_row("revenue (ledger)", f"{revenue_bal} Athel")
    table.add_row("escrow (ledger)", f"{escrow_bal} Athel")
    table.add_row("listing attivi", str(n_listings))
    table.add_row("ordini totali", str(n_orders))
    if warehouse is not None:
        table.add_row("─── warehouse ───", "")
        table.add_row("code", warehouse.code)
        table.add_row("depth_meters", str(warehouse.depth_meters))
        table.add_row(
            "used_capacity",
            f"{warehouse.used_capacity} / {warehouse.capacity}",
        )
        table.add_row("access_location_id", str(warehouse.access_location_id or "—"))
    console.print(table)

    # Commission rates
    raw = (platform.metadata_json or {}).get("commission_rates")
    if isinstance(raw, dict):
        rate_table = Table(title="Commissioni per (seller_type, product_type)")
        rate_table.add_column("Seller", style="cyan")
        rate_table.add_column("Product", style="green")
        rate_table.add_column("Rate", justify="right", style="yellow")
        for seller_type, mapping in sorted(raw.items()):
            if not isinstance(mapping, dict):
                continue
            for product_type, rate in sorted(mapping.items()):
                try:
                    rate_f = float(rate)
                except (TypeError, ValueError):
                    continue
                rate_table.add_row(seller_type, product_type, f"{rate_f:.2%}")
        console.print(rate_table)


# ---------------------------------------------------------------------------
# listings
# ---------------------------------------------------------------------------


@aion_app.command("listings")
def aion_listings(
    status: str | None = typer.Option(None, "--status", "-s", help="ACTIVE/SOLD_OUT/CANCELLED."),
    seller_type: str | None = typer.Option(None, "--seller-type", help="CHARACTER/COMPANY/..."),
    product_type: str | None = typer.Option(None, "--product-type", help="GOODS/SERVICE/LOT/..."),
    limit: int = typer.Option(50, "--limit", "-l", min=1, max=500),
) -> None:
    """Elenca i listing AION."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        stmt = select(AionListing).order_by(AionListing.id.desc()).limit(limit)
        if status is not None:
            try:
                st = AionListingStatus(status.upper())
            except ValueError:
                valid = ", ".join(x.value for x in AionListingStatus)
                console.print(f"[red]Status non valido. Validi: {valid}[/]")
                raise typer.Exit(code=1) from None
            stmt = stmt.where(AionListing.status == st.value)
        if seller_type is not None:
            try:
                se = AionSellerType(seller_type.upper())
            except ValueError:
                valid = ", ".join(x.value for x in AionSellerType)
                console.print(f"[red]Seller type non valido. Validi: {valid}[/]")
                raise typer.Exit(code=1) from None
            stmt = stmt.where(AionListing.seller_type == se.value)
        if product_type is not None:
            try:
                pt = AionProductType(product_type.upper())
            except ValueError:
                valid = ", ".join(x.value for x in AionProductType)
                console.print(f"[red]Product type non valido. Validi: {valid}[/]")
                raise typer.Exit(code=1) from None
            stmt = stmt.where(AionListing.product_type == pt.value)

        listings = list(session.scalars(stmt))
        rows: list[dict[str, object]] = []
        for listing in listings:
            seller_name = _resolve_seller_name(session, listing)
            rows.append(
                {
                    "id": listing.id,
                    "seller_type": listing.seller_type,
                    "seller_id": listing.seller_id,
                    "seller_name": seller_name,
                    "product_type": listing.product_type,
                    "item_type": listing.item_type,
                    "item_name": listing.item_name,
                    "unit_price": listing.unit_price,
                    "remaining": listing.remaining_quantity,
                    "quantity": listing.quantity,
                    "status": listing.status,
                    "mode": listing.fulfillment_mode,
                }
            )

    if not rows:
        console.print("[yellow]Nessun listing.[/]")
        return

    table = Table(title=f"Listing AION ({len(rows)})")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Seller", style="magenta")
    table.add_column("Product", style="green")
    table.add_column("Item", style="yellow")
    table.add_column("Nome", style="dim")
    table.add_column("Prezzo", justify="right", style="blue")
    table.add_column("Stock", justify="right")
    table.add_column("Status", style="red")
    table.add_column("Mode", style="dim")
    for r in rows:
        table.add_row(
            str(r["id"]),
            f"{r['seller_type']}:{r['seller_name']}",
            str(r["product_type"]),
            str(r["item_type"]),
            str(r["item_name"]),
            str(r["unit_price"]),
            f"{r['remaining']}/{r['quantity']}",
            str(r["status"]),
            str(r["mode"]),
        )
    console.print(table)


@aion_app.command("listing")
def aion_listing(listing_id: int = typer.Argument(..., help="ID del listing.")) -> None:
    """Dettaglio di un listing + ordini collegati."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        listing = AionService.get_listing(session, listing_id)
        if listing is None:
            console.print(f"[red]Listing id={listing_id} non trovato.[/]")
            raise typer.Exit(code=1)

        seller_name = _resolve_seller_name(session, listing)
        orders = AionService.orders_of_listing(session, listing_id)
        order_rows: list[tuple[int, str, int, int, str]] = []
        for o in orders:
            order_rows.append((o.id, o.buyer_type, o.buyer_id, o.total_price, o.status))

    table = Table(title=f"Listing #{listing.id}")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("seller_type", listing.seller_type)
    table.add_row("seller_id", str(listing.seller_id))
    table.add_row("seller_name", seller_name)
    table.add_row("product_type", listing.product_type)
    table.add_row("item_type", listing.item_type)
    table.add_row("item_name", listing.item_name)
    table.add_row("unit_price", f"{listing.unit_price} Athel")
    table.add_row("quantity", f"{listing.quantity_sold}/{listing.quantity}")
    table.add_row("remaining", str(listing.remaining_quantity))
    table.add_row("condition", f"{listing.condition:.2f}")
    table.add_row("quality_label", listing.quality_label or "—")
    table.add_row("fulfillment_mode", listing.fulfillment_mode)
    table.add_row("status", listing.status)
    table.add_row("source_object_id", str(listing.source_object_id or "—"))
    table.add_row("lot_id", str(listing.lot_id or "—"))
    table.add_row("vehicle_id", str(listing.vehicle_id or "—"))
    table.add_row("warehouse_id", str(listing.warehouse_id or "—"))
    table.add_row("description", listing.description or "—")
    console.print(table)

    if order_rows:
        ot = Table(title=f"Ordini sul listing ({len(order_rows)})")
        ot.add_column("ID", style="cyan", justify="right")
        ot.add_column("Buyer", style="magenta")
        ot.add_column("Buyer ID", justify="right")
        ot.add_column("Totale", justify="right", style="blue")
        ot.add_column("Status", style="green")
        for oid, btype, bid, total, st in order_rows:
            ot.add_row(str(oid), btype, str(bid), str(total), st)
        console.print(ot)
    else:
        console.print("[dim]Nessun ordine su questo listing.[/]")


# ---------------------------------------------------------------------------
# orders
# ---------------------------------------------------------------------------


@aion_app.command("orders")
def aion_orders(
    status: str | None = typer.Option(None, "--status", "-s"),
    buyer_type: str | None = typer.Option(None, "--buyer-type"),
    buyer_id: int | None = typer.Option(None, "--buyer-id"),
    limit: int = typer.Option(50, "--limit", "-l", min=1, max=500),
) -> None:
    """Elenca gli ordini AION."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        stmt = select(AionOrder).order_by(AionOrder.id.desc()).limit(limit)
        if status is not None:
            try:
                st = AionOrderStatus(status.upper())
            except ValueError:
                valid = ", ".join(x.value for x in AionOrderStatus)
                console.print(f"[red]Status non valido. Validi: {valid}[/]")
                raise typer.Exit(code=1) from None
            stmt = stmt.where(AionOrder.status == st.value)
        if buyer_type is not None:
            try:
                bt = AionBuyerType(buyer_type.upper())
            except ValueError:
                valid = ", ".join(x.value for x in AionBuyerType)
                console.print(f"[red]Buyer type non valido. Validi: {valid}[/]")
                raise typer.Exit(code=1) from None
            stmt = stmt.where(AionOrder.buyer_type == bt.value)
        if buyer_id is not None:
            stmt = stmt.where(AionOrder.buyer_id == buyer_id)

        orders = list(session.scalars(stmt))
        rows: list[dict[str, object]] = []
        for o in orders:
            listing = AionService.get_listing(session, o.listing_id)
            rows.append(
                {
                    "id": o.id,
                    "buyer": f"{o.buyer_type}:{o.buyer_id}",
                    "listing_id": o.listing_id,
                    "item_name": listing.item_name if listing else "?",
                    "quantity": o.quantity,
                    "total": o.total_price,
                    "commission": o.commission,
                    "net": o.net_to_seller,
                    "status": o.status,
                }
            )

    if not rows:
        console.print("[yellow]Nessun ordine.[/]")
        return

    table = Table(title=f"Ordini AION ({len(rows)})")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Buyer", style="magenta")
    table.add_column("Listing", justify="right")
    table.add_column("Item", style="yellow")
    table.add_column("Qty", justify="right")
    table.add_column("Totale", justify="right", style="blue")
    table.add_column("Comm.", justify="right", style="dim")
    table.add_column("Netto", justify="right", style="green")
    table.add_column("Status", style="red")
    for r in rows:
        table.add_row(
            str(r["id"]),
            str(r["buyer"]),
            str(r["listing_id"]),
            str(r["item_name"]),
            str(r["quantity"]),
            str(r["total"]),
            str(r["commission"]),
            str(r["net"]),
            str(r["status"]),
        )
    console.print(table)


@aion_app.command("order")
def aion_order(order_id: int = typer.Argument(..., help="ID dell'ordine.")) -> None:
    """Dettaglio di un ordine + spedizione collegata + entry ledger."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        order = AionService.get_order(session, order_id)
        if order is None:
            console.print(f"[red]Ordine id={order_id} non trovato.[/]")
            raise typer.Exit(code=1)

        listing = AionService.get_listing(session, order.listing_id)
        shipment = session.scalars(
            select(AionShipment).where(AionShipment.order_id == order.id)
        ).first()

    table = Table(title=f"Ordine AION #{order.id}")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("listing_id", str(order.listing_id))
    table.add_row("item_name", listing.item_name if listing else "?")
    table.add_row("buyer_type", order.buyer_type)
    table.add_row("buyer_id", str(order.buyer_id))
    table.add_row("quantity", str(order.quantity))
    table.add_row("unit_price", str(order.unit_price))
    table.add_row("total_price", str(order.total_price))
    table.add_row("commission", str(order.commission))
    table.add_row("net_to_seller", str(order.net_to_seller))
    table.add_row("escrowed_amount", str(order.escrowed_amount))
    table.add_row("escrow_entry_id", str(order.escrow_entry_id or "—"))
    table.add_row("settlement_entry_id", str(order.settlement_entry_id or "—"))
    table.add_row("status", order.status)
    table.add_row("created_at", str(order.created_at_total_seconds))
    table.add_row("delivered_at", str(order.delivered_at_total_seconds or "—"))
    console.print(table)

    if shipment is not None:
        st = Table(title=f"Spedizione #{shipment.id}")
        st.add_column("Chiave", style="cyan", no_wrap=True)
        st.add_column("Valore", style="magenta")
        st.add_row("mode", shipment.mode)
        st.add_row("status", shipment.status)
        st.add_row("distance_cells", f"{shipment.distance_cells:.2f}")
        st.add_row("duration_ticks", str(shipment.duration_ticks))
        st.add_row("shipping_cost", str(shipment.shipping_cost))
        st.add_row("origin_location_id", str(shipment.origin_location_id or "—"))
        st.add_row("destination_location_id", str(shipment.destination_location_id or "—"))
        st.add_row("started_at", str(shipment.started_at_total_seconds))
        st.add_row("arrives_at", str(shipment.arrives_at_total_seconds))
        st.add_row("delivered_at", str(shipment.delivered_at_total_seconds or "—"))
        console.print(st)


# ---------------------------------------------------------------------------
# Azioni: ship / settle / cancel
# ---------------------------------------------------------------------------


@aion_app.command("ship")
def aion_ship(order_id: int = typer.Argument(..., help="ID dell'ordine.")) -> None:
    """Forza `ship_order` su un ordine ESCROWED."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        order = AionService.get_order(session, order_id)
        if order is None:
            console.print(f"[red]Ordine id={order_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            result = AionService.ship_order(
                session, order=order, current_dt=build_starting_datetime()
            )
        except AionError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        if result.ok:
            session.commit()

    table = Table(title=f"ship_order #{order_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("ok", str(result.ok))
    table.add_row("reason", result.reason)
    table.add_row("shipment_id", str(result.shipment_id or "—"))
    table.add_row("mode", result.mode or "—")
    table.add_row("duration_ticks", str(result.duration_ticks))
    table.add_row("distance_cells", f"{result.distance_cells:.2f}")
    table.add_row("immediate", str(result.immediate))
    console.print(table)
    if not result.ok:
        raise typer.Exit(code=1)


@aion_app.command("settle")
def aion_settle(order_id: int = typer.Argument(..., help="ID dell'ordine.")) -> None:
    """Forza `confirm_delivery` su un ordine ESCROWED o SHIPPED."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        order = AionService.get_order(session, order_id)
        if order is None:
            console.print(f"[red]Ordine id={order_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            result = AionService.confirm_delivery(
                session, order=order, current_dt=build_starting_datetime()
            )
        except AionError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        if result.ok:
            session.commit()

    table = Table(title=f"confirm_delivery #{order_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("ok", str(result.ok))
    table.add_row("reason", result.reason)
    table.add_row("settled_amount", str(result.settled_amount))
    table.add_row("commission", str(result.commission))
    table.add_row("settlement_entry_id", str(result.settlement_entry_id or "—"))
    console.print(table)
    if not result.ok:
        raise typer.Exit(code=1)


@aion_app.command("cancel")
def aion_cancel(order_id: int = typer.Argument(..., help="ID dell'ordine.")) -> None:
    """Forza `cancel_order` (refund) su un ordine ESCROWED o PENDING."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        order = AionService.get_order(session, order_id)
        if order is None:
            console.print(f"[red]Ordine id={order_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            result = AionService.cancel_order(
                session, order=order, current_dt=build_starting_datetime()
            )
        except AionError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        if result.ok:
            session.commit()

    table = Table(title=f"cancel_order #{order_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("ok", str(result.ok))
    table.add_row("reason", result.reason)
    table.add_row("settled_amount", str(result.settled_amount))
    table.add_row("settlement_entry_id", str(result.settlement_entry_id or "—"))
    console.print(table)
    if not result.ok:
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# warehouse
# ---------------------------------------------------------------------------


@aion_app.command("warehouse")
def aion_warehouse(
    code: str = typer.Option("aion:warehouse:global", "--code", "-c", help="Codice magazzino."),
) -> None:
    """Stato di un magazzino AION + inventario."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        AionService.ensure_platform(session)
        session.commit()
        warehouse = session.scalars(select(AionWarehouse).where(AionWarehouse.code == code)).first()
        if warehouse is None:
            console.print(f"[red]Magazzino {code!r} non trovato.[/]")
            raise typer.Exit(code=1)
        items = list(
            session.scalars(
                select(AionInventoryItem)
                .where(AionInventoryItem.warehouse_id == warehouse.id)
                .order_by(AionInventoryItem.id)
            )
        )
        rows: list[tuple[int, str, str, int, str, str]] = [
            (i.id, i.item_type, i.item_name, i.quantity, i.condition.__format__(".2f"), i.status)
            for i in items
        ]

    table = Table(title=f"Magazzino AION — {warehouse.name}")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("code", warehouse.code)
    table.add_row("kind", warehouse.warehouse_kind)
    table.add_row("depth_meters", str(warehouse.depth_meters))
    table.add_row("capacity", str(warehouse.capacity))
    table.add_row("used_capacity", str(warehouse.used_capacity))
    table.add_row(
        "riempimento",
        f"{(warehouse.used_capacity / warehouse.capacity) * 100:.1f}%"
        if warehouse.capacity > 0
        else "—",
    )
    table.add_row("access_location_id", str(warehouse.access_location_id or "—"))
    table.add_row("is_active", "✓" if warehouse.is_active else "✗")
    console.print(table)

    if rows:
        it = Table(title=f"Inventario ({len(rows)})")
        it.add_column("ID", style="cyan", justify="right")
        it.add_column("Item", style="green")
        it.add_column("Nome", style="magenta")
        it.add_column("Qty", justify="right")
        it.add_column("Cond", justify="right")
        it.add_column("Status", style="yellow")
        for iid, itype, iname, qty, cond, status in rows:
            it.add_row(str(iid), itype, iname, str(qty), cond, status)
        console.print(it)
    else:
        console.print("[dim]Nessun item stoccato.[/]")


# ---------------------------------------------------------------------------
# tick
# ---------------------------------------------------------------------------


@aion_app.command("tick")
def aion_tick(
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
    with_ai: bool = typer.Option(
        True,
        "--ai/--no-ai",
        help="Esegue anche AionAI.daily_tick (listing + ordini).",
    ),
) -> None:
    """Forza un tick AION: spedizioni + (opzionale) attività AI."""
    _require_migrated()
    from simai.core.time_manager import TimeManager

    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        AionService.ensure_platform(session)

        ship_report = AionService.tick_shipments(session, current_dt=current)
        ai_summary = None
        if with_ai:
            from simai.economy.aion import AionAI

            rng = random.Random(settings.master_seed + at_tick)
            ai_summary = AionAI.daily_tick(session, current_dt=current, rng=rng)
        session.commit()

    table = Table(title=f"AION tick @ {current}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("shipments_completed", str(ship_report.deliveries_completed))
    table.add_row("shipments_failed", str(ship_report.shipments_failed))
    if ai_summary is not None:
        table.add_row("ai.sellers", str(ai_summary.sellers_evaluated))
        table.add_row("ai.buyers", str(ai_summary.buyers_evaluated))
        table.add_row("ai.listings", str(ai_summary.listings_created))
        table.add_row("ai.orders", str(ai_summary.orders_placed))
        table.add_row("ai.orders_failed", str(ai_summary.orders_failed))
        table.add_row("ai.shipments_delivered", str(ai_summary.shipments_delivered))
        table.add_row("ai.errors", str(len(ai_summary.errors)))
    console.print(table)


# ---------------------------------------------------------------------------
# seed
# ---------------------------------------------------------------------------


@aion_app.command("seed")
def aion_seed(
    n_sellers: int = typer.Option(6, "--sellers", "-s", min=1, max=50),
    items_per_seller: int = typer.Option(2, "--items", "-i", min=1, max=10),
) -> None:
    """Popola AION con listing demo (idempotente)."""
    _require_migrated()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        result = seed_demo_aion(
            session,
            current_dt=start,
            n_sellers=n_sellers,
            items_per_seller=items_per_seller,
        )
        session.commit()

    if result.reason == "already_seeded":
        console.print("[yellow]AION già popolata — nessuna azione.[/]")
        return
    if result.reason == "no_sellers":
        console.print("[red]Nessun NPC con saldo sufficiente.[/] [dim]Esegui `npc seed`.[/]")
        raise typer.Exit(code=1)

    table = Table(title="Seed AION")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("sellers_processed", str(result.sellers_processed))
    table.add_row("objects_created", str(result.objects_created))
    table.add_row("listings_created", str(result.listings_created))
    table.add_row("orders_placed", str(result.orders_placed))
    table.add_row("shipments_delivered", str(result.shipments_delivered))
    table.add_row("errors", str(len(result.errors)))
    table.add_row("reason", result.reason)
    console.print(table)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_seller_name(session: object, listing: AionListing) -> str:
    """Risolve il nome del seller (Character o Company)."""
    from sqlalchemy.orm import Session as _Session

    assert isinstance(session, _Session)
    if listing.seller_type == AionSellerType.CHARACTER.value and listing.seller_character_id:
        char = session.get(Character, listing.seller_character_id)
        return char.full_name if char else f"<char:{listing.seller_character_id}>"
    if listing.seller_type == AionSellerType.COMPANY.value and listing.seller_company_id:
        from simai.economy.companies.models import Company as _Company

        comp = session.get(_Company, listing.seller_company_id)
        return comp.name if comp else f"<company:{listing.seller_company_id}>"
    return f"<{listing.seller_type}:{listing.seller_id}>"


def register(parent: typer.Typer) -> None:
    """Registra `aion_app` come sottocomando di `economy`."""
    parent.add_typer(aion_app, name="aion")


__all__ = ["aion_app", "register"]
