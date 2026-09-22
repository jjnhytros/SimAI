"""Operazioni su District e Lot."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.world.district import District, DistrictSummary
from simai.world.enums import DistrictType, LotUsage
from simai.world.lot import Lot, LotSummary

# ---------------------------------------------------------------------------
# District
# ---------------------------------------------------------------------------


def create_district(
    session: Session,
    *,
    name: str,
    type_: DistrictType = DistrictType.MIXED,
    bounds: tuple[int, int, int, int] = (0, 0, 50, 50),
    tax_rate: float = 0.05,
    safety_rating: float = 0.5,
    aesthetic_score: float = 0.5,
    metadata: dict[str, Any] | None = None,
) -> District:
    """Crea e persiste un District."""
    if not (0.0 <= tax_rate <= 1.0):
        raise ValueError(f"tax_rate deve essere in [0, 1], ricevuto {tax_rate}")
    if not (0.0 <= safety_rating <= 1.0):
        raise ValueError(f"safety_rating deve essere in [0, 1], ricevuto {safety_rating}")
    if not (0.0 <= aesthetic_score <= 1.0):
        raise ValueError(f"aesthetic_score deve essere in [0, 1], ricevuto {aesthetic_score}")
    x, y, w, h = bounds
    d = District(
        name=name,
        type=type_.value,
        bounds_x=x,
        bounds_y=y,
        bounds_w=w,
        bounds_h=h,
        tax_rate=tax_rate,
        safety_rating=safety_rating,
        aesthetic_score=aesthetic_score,
        metadata_json=dict(metadata or {}),
    )
    session.add(d)
    session.flush()
    return d


def get_district(session: Session, district_id: int) -> District | None:
    return session.get(District, district_id)


def list_districts(session: Session) -> list[District]:
    return list(session.scalars(select(District).order_by(District.id)))


def district_summaries(session: Session) -> list[DistrictSummary]:
    """Lista di DistrictSummary con conteggio lotti."""
    districts = list_districts(session)
    # Conteggio lotti per district in una query
    rows = session.execute(select(Lot.district_id, func.count()).group_by(Lot.district_id)).all()
    counts: dict[int, int] = {int(did): int(cnt) for did, cnt in rows}
    return [
        DistrictSummary(
            id=d.id,
            name=d.name,
            type=d.type,
            bounds=(d.bounds_x, d.bounds_y, d.bounds_w, d.bounds_h),
            tax_rate=d.tax_rate,
            lot_count=counts.get(d.id, 0),
        )
        for d in districts
    ]


# ---------------------------------------------------------------------------
# Lot
# ---------------------------------------------------------------------------


def create_lot(
    session: Session,
    *,
    district_id: int,
    name: str,
    usage: LotUsage = LotUsage.VACANT,
    bounds: tuple[int, int, int, int] = (0, 0, 10, 10),
    base_price: int = 1000,
    location_id: int | None = None,
    is_developed: bool = False,
    metadata: dict[str, Any] | None = None,
) -> Lot:
    """Crea e persiste un Lot."""
    if base_price < 0:
        raise ValueError(f"base_price deve essere >= 0, ricevuto {base_price}")
    if session.get(District, district_id) is None:
        raise LookupError(f"District id={district_id} non trovato")
    x, y, w, h = bounds
    lot = Lot(
        district_id=district_id,
        name=name,
        usage=usage.value,
        bounds_x=x,
        bounds_y=y,
        bounds_w=w,
        bounds_h=h,
        base_price=base_price,
        location_id=location_id,
        is_developed=is_developed,
        metadata_json=dict(metadata or {}),
        current_value=float(base_price),
    )
    session.add(lot)
    session.flush()
    return lot


def get_lot(session: Session, lot_id: int) -> Lot | None:
    return session.get(Lot, lot_id)


def list_lots(session: Session, *, district_id: int | None = None) -> list[Lot]:
    stmt = select(Lot).order_by(Lot.id)
    if district_id is not None:
        stmt = stmt.where(Lot.district_id == district_id)
    return list(session.scalars(stmt))


def lot_summaries(session: Session, *, district_id: int | None = None) -> list[LotSummary]:
    lots = list_lots(session, district_id=district_id)
    return [
        LotSummary(
            id=lot.id,
            name=lot.name,
            district_id=lot.district_id,
            usage=lot.usage,
            bounds=(lot.bounds_x, lot.bounds_y, lot.bounds_w, lot.bounds_h),
            base_price=lot.base_price,
            is_developed=lot.is_developed,
            location_id=lot.location_id,
        )
        for lot in lots
    ]


def attach_location(session: Session, *, lot_id: int, location_id: int) -> Lot:
    """Collega una Location come edificio "centrale" del Lot."""
    lot = get_lot(session, lot_id)
    if lot is None:
        raise LookupError(f"Lot id={lot_id} non trovato")
    lot.location_id = location_id
    lot.is_developed = True
    session.flush()
    return lot


def update_lot_usage(session: Session, *, lot_id: int, usage: LotUsage) -> Lot:
    lot = get_lot(session, lot_id)
    if lot is None:
        raise LookupError(f"Lot id={lot_id} non trovato")
    lot.usage = usage.value
    session.flush()
    return lot


def lot_bounds_summary(lot: Lot) -> dict[str, int]:
    """Ritorna bounds in formato dict per UI."""
    return {
        "x": lot.bounds_x,
        "y": lot.bounds_y,
        "w": lot.bounds_w,
        "h": lot.bounds_h,
    }


__all__ = [
    "attach_location",
    "create_district",
    "create_lot",
    "district_summaries",
    "get_district",
    "get_lot",
    "list_districts",
    "list_lots",
    "lot_bounds_summary",
    "lot_summaries",
    "update_lot_usage",
]
