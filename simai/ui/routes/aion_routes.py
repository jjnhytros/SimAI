"""Route: AION (marketplace multivendor) — read-only."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.economy.aion import (
    AION_ESCROW_CODE,
    AION_REVENUE_CODE,
    AionBuyerType,
    AionInventoryItem,
    AionListing,
    AionListingStatus,
    AionOrder,
    AionOrderStatus,
    AionProductType,
    AionSellerType,
    AionService,
    AionShipment,
    AionShipmentStatus,
    AionWarehouse,
)
from simai.economy.companies.models import Company
from simai.economy.ledger import LedgerService
from simai.npc.models import Character
from simai.ui.app import templates
from simai.ui.deps import get_db

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_seller_name(session: Session, listing: AionListing) -> str:
    """Risolve il nome del seller (Character o Company)."""
    if listing.seller_type == AionSellerType.CHARACTER.value and listing.seller_character_id:
        char = session.get(Character, listing.seller_character_id)
        return char.full_name if char else f"<char:{listing.seller_character_id}>"
    if listing.seller_type == AionSellerType.COMPANY.value and listing.seller_company_id:
        comp = session.get(Company, listing.seller_company_id)
        return comp.name if comp else f"<company:{listing.seller_company_id}>"
    return f"<{listing.seller_type}:{listing.seller_id}>"


def _resolve_buyer_name(session: Session, order: AionOrder) -> tuple[str, int | None]:
    """Ritorna `(display_name, link_character_id_or_None)`."""
    if order.buyer_type == AionBuyerType.CHARACTER.value and order.buyer_character_id:
        char = session.get(Character, order.buyer_character_id)
        if char is not None:
            return (char.full_name, char.id)
        return (f"<char:{order.buyer_character_id}>", None)
    if order.buyer_type == AionBuyerType.COMPANY.value and order.buyer_company_id:
        comp = session.get(Company, order.buyer_company_id)
        if comp is not None:
            return (comp.name, None)
        return (f"<company:{order.buyer_company_id}>", None)
    return (f"<{order.buyer_type}:{order.buyer_id}>", None)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@router.get("/economy/aion", response_class=HTMLResponse)
def aion_dashboard(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dashboard AION: platform, revenue/escrow, contatori, magazzino globale."""
    AionService.ensure_platform(session)
    session.commit()

    platform = AionService.get_platform(session)
    warehouse = AionService.get_global_warehouse(session)

    revenue_acc = LedgerService.get_account(session, AION_REVENUE_CODE)
    escrow_acc = LedgerService.get_account(session, AION_ESCROW_CODE)
    revenue_bal = LedgerService.get_signed_balance(session, revenue_acc) if revenue_acc else 0
    escrow_bal = -LedgerService.get_signed_balance(session, escrow_acc) if escrow_acc else 0

    n_active_listings = int(
        session.scalar(
            select(func.count())
            .select_from(AionListing)
            .where(AionListing.status == AionListingStatus.ACTIVE.value)
        )
        or 0
    )
    n_sold_out = int(
        session.scalar(
            select(func.count())
            .select_from(AionListing)
            .where(AionListing.status == AionListingStatus.SOLD_OUT.value)
        )
        or 0
    )
    n_orders = int(session.scalar(select(func.count()).select_from(AionOrder)) or 0)
    n_orders_escrowed = int(
        session.scalar(
            select(func.count())
            .select_from(AionOrder)
            .where(AionOrder.status == AionOrderStatus.ESCROWED.value)
        )
        or 0
    )
    n_orders_shipped = int(
        session.scalar(
            select(func.count())
            .select_from(AionOrder)
            .where(AionOrder.status == AionOrderStatus.SHIPPED.value)
        )
        or 0
    )
    n_orders_delivered = int(
        session.scalar(
            select(func.count())
            .select_from(AionOrder)
            .where(AionOrder.status == AionOrderStatus.DELIVERED.value)
        )
        or 0
    )
    n_shipments_transit = int(
        session.scalar(
            select(func.count())
            .select_from(AionShipment)
            .where(AionShipment.status == AionShipmentStatus.IN_TRANSIT.value)
        )
        or 0
    )

    # Ultimi 10 listing e ordini
    recent_listings = list(
        session.scalars(select(AionListing).order_by(AionListing.id.desc()).limit(10))
    )
    recent_orders = list(session.scalars(select(AionOrder).order_by(AionOrder.id.desc()).limit(10)))

    listing_rows = [
        {
            "id": lst.id,
            "seller_type": lst.seller_type,
            "seller_name": _resolve_seller_name(session, lst),
            "product_type": lst.product_type,
            "item_name": lst.item_name,
            "unit_price": lst.unit_price,
            "remaining": lst.remaining_quantity,
            "quantity": lst.quantity,
            "status": lst.status,
        }
        for lst in recent_listings
    ]

    order_rows = []
    for o in recent_orders:
        listing = AionService.get_listing(session, o.listing_id)
        buyer_name, buyer_link = _resolve_buyer_name(session, o)
        order_rows.append(
            {
                "id": o.id,
                "buyer_name": buyer_name,
                "buyer_link": buyer_link,
                "listing_id": o.listing_id,
                "item_name": listing.item_name if listing else "?",
                "quantity": o.quantity,
                "total": o.total_price,
                "status": o.status,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_aion_dashboard.html",
        {
            "platform": platform,
            "warehouse": warehouse,
            "revenue_balance": revenue_bal,
            "escrow_balance": escrow_bal,
            "n_active_listings": n_active_listings,
            "n_sold_out": n_sold_out,
            "n_orders": n_orders,
            "n_orders_escrowed": n_orders_escrowed,
            "n_orders_shipped": n_orders_shipped,
            "n_orders_delivered": n_orders_delivered,
            "n_shipments_transit": n_shipments_transit,
            "recent_listings": listing_rows,
            "recent_orders": order_rows,
        },
    )


# ---------------------------------------------------------------------------
# Listings
# ---------------------------------------------------------------------------


@router.get("/economy/aion/listings", response_class=HTMLResponse)
def aion_listings(
    request: Request,
    session: Session = Depends(get_db),
    status: str = Query(default="ACTIVE"),
    seller_type: str = Query(default=""),
    product_type: str = Query(default=""),
    limit: int = Query(default=200, ge=1, le=1000),
) -> HTMLResponse:
    """Lista listing con filtri base."""
    stmt = select(AionListing).order_by(AionListing.id.desc()).limit(limit)

    if status and status.upper() != "ALL":
        try:
            st = AionListingStatus(status.upper())
        except ValueError:
            st = AionListingStatus.ACTIVE
        stmt = stmt.where(AionListing.status == st.value)

    if seller_type:
        try:
            se = AionSellerType(seller_type.upper())
            stmt = stmt.where(AionListing.seller_type == se.value)
        except ValueError:
            pass

    if product_type:
        try:
            pt = AionProductType(product_type.upper())
            stmt = stmt.where(AionListing.product_type == pt.value)
        except ValueError:
            pass

    listings = list(session.scalars(stmt))
    rows = [
        {
            "id": lst.id,
            "seller_type": lst.seller_type,
            "seller_name": _resolve_seller_name(session, lst),
            "product_type": lst.product_type,
            "item_type": lst.item_type,
            "item_name": lst.item_name,
            "unit_price": lst.unit_price,
            "remaining": lst.remaining_quantity,
            "quantity": lst.quantity,
            "condition": lst.condition,
            "fulfillment_mode": lst.fulfillment_mode,
            "status": lst.status,
        }
        for lst in listings
    ]

    return templates.TemplateResponse(
        request,
        "economy_aion_listings.html",
        {
            "listings": rows,
            "status": status,
            "seller_type": seller_type,
            "product_type": product_type,
            "limit": limit,
            "statuses": [s.value for s in AionListingStatus],
            "seller_types": [s.value for s in AionSellerType],
            "product_types": [p.value for p in AionProductType],
        },
    )


@router.get("/economy/aion/listings/{listing_id}", response_class=HTMLResponse)
def aion_listing_detail(
    request: Request,
    listing_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio di un listing + ordini collegati."""
    listing = AionService.get_listing(session, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail=f"Listing {listing_id} non trovato")

    seller_name = _resolve_seller_name(session, listing)
    orders = AionService.orders_of_listing(session, listing_id)
    order_rows = []
    for o in orders:
        buyer_name, buyer_link = _resolve_buyer_name(session, o)
        order_rows.append(
            {
                "id": o.id,
                "buyer_name": buyer_name,
                "buyer_link": buyer_link,
                "quantity": o.quantity,
                "total": o.total_price,
                "commission": o.commission,
                "net": o.net_to_seller,
                "status": o.status,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_aion_listing_detail.html",
        {
            "listing": listing,
            "seller_name": seller_name,
            "orders": order_rows,
        },
    )


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------


@router.get("/economy/aion/orders", response_class=HTMLResponse)
def aion_orders(
    request: Request,
    session: Session = Depends(get_db),
    status: str = Query(default=""),
    buyer_type: str = Query(default=""),
    limit: int = Query(default=200, ge=1, le=1000),
) -> HTMLResponse:
    """Lista ordini con filtri base."""
    stmt = select(AionOrder).order_by(AionOrder.id.desc()).limit(limit)

    if status and status.upper() != "ALL":
        try:
            st = AionOrderStatus(status.upper())
            stmt = stmt.where(AionOrder.status == st.value)
        except ValueError:
            pass

    if buyer_type:
        try:
            bt = AionBuyerType(buyer_type.upper())
            stmt = stmt.where(AionOrder.buyer_type == bt.value)
        except ValueError:
            pass

    orders = list(session.scalars(stmt))
    rows = []
    for o in orders:
        listing = AionService.get_listing(session, o.listing_id)
        buyer_name, buyer_link = _resolve_buyer_name(session, o)
        rows.append(
            {
                "id": o.id,
                "buyer_type": o.buyer_type,
                "buyer_name": buyer_name,
                "buyer_link": buyer_link,
                "listing_id": o.listing_id,
                "item_name": listing.item_name if listing else "?",
                "quantity": o.quantity,
                "total": o.total_price,
                "commission": o.commission,
                "net": o.net_to_seller,
                "status": o.status,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_aion_orders.html",
        {
            "orders": rows,
            "status": status,
            "buyer_type": buyer_type,
            "limit": limit,
            "statuses": [s.value for s in AionOrderStatus],
            "buyer_types": [b.value for b in AionBuyerType],
        },
    )


@router.get("/economy/aion/orders/{order_id}", response_class=HTMLResponse)
def aion_order_detail(
    request: Request,
    order_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio di un ordine + spedizione + entry ledger."""
    order = AionService.get_order(session, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Ordine {order_id} non trovato")

    listing = AionService.get_listing(session, order.listing_id)
    shipment = session.scalars(
        select(AionShipment).where(AionShipment.order_id == order.id)
    ).first()
    buyer_name, buyer_link = _resolve_buyer_name(session, order)

    return templates.TemplateResponse(
        request,
        "economy_aion_order_detail.html",
        {
            "order": order,
            "listing": listing,
            "shipment": shipment,
            "buyer_name": buyer_name,
            "buyer_link": buyer_link,
        },
    )


# ---------------------------------------------------------------------------
# Warehouse
# ---------------------------------------------------------------------------


@router.get("/economy/aion/warehouse", response_class=HTMLResponse)
def aion_warehouse(
    request: Request,
    session: Session = Depends(get_db),
    code: str = Query(default="aion:warehouse:global"),
) -> HTMLResponse:
    """Stato magazzini AION + inventario."""
    AionService.ensure_platform(session)
    session.commit()

    warehouses = list(session.scalars(select(AionWarehouse).order_by(AionWarehouse.id)))
    selected = next((w for w in warehouses if w.code == code), None)

    items: list[dict[str, object]] = []
    if selected is not None:
        rows = list(
            session.scalars(
                select(AionInventoryItem)
                .where(AionInventoryItem.warehouse_id == selected.id)
                .order_by(AionInventoryItem.id)
            )
        )
        items = [
            {
                "id": i.id,
                "item_type": i.item_type,
                "item_name": i.item_name,
                "quantity": i.quantity,
                "condition": i.condition,
                "quality_label": i.quality_label,
                "status": i.status,
            }
            for i in rows
        ]

    return templates.TemplateResponse(
        request,
        "economy_aion_warehouse.html",
        {
            "warehouses": warehouses,
            "selected": selected,
            "items": items,
            "code": code,
        },
    )


__all__ = ["router"]
