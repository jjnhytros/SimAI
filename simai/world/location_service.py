"""Operazioni di alto livello su Location."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.world.enums import EdgeKind, LocationType
from simai.world.models import GameObject, Location, LocationEdge


def create_location(
    session: Session,
    *,
    name: str,
    type_: LocationType = LocationType.ROOM,
    parent_id: int | None = None,
    lot_id: int | None = None,
    bounds: tuple[int, int, int, int] = (0, 0, 1, 1),
    capacity: int = 10,
) -> Location:
    """Crea e persiste una nuova Location. Ritorna l'istanza con `id` popolato."""
    if capacity < 0:
        raise ValueError(f"capacity deve essere >= 0, ricevuto {capacity}")
    x, y, w, h = bounds
    loc = Location(
        name=name,
        type=str(type_),
        parent_id=parent_id,
        lot_id=lot_id,
        bounds_x=x,
        bounds_y=y,
        bounds_w=w,
        bounds_h=h,
        capacity=capacity,
    )
    session.add(loc)
    session.flush()
    return loc


def add_edge(
    session: Session,
    *,
    from_id: int,
    to_id: int,
    kind: EdgeKind = EdgeKind.DOOR,
    distance: float = 1.0,
    bidirectional: bool = True,
    accessible: bool = True,
) -> LocationEdge:
    """Crea e persiste un arco tra due Location."""
    if from_id == to_id:
        raise ValueError("from_id e to_id devono essere diversi")
    if distance <= 0:
        raise ValueError(f"distance deve essere > 0, ricevuto {distance}")
    edge = LocationEdge(
        from_location_id=from_id,
        to_location_id=to_id,
        kind=str(kind),
        distance=distance,
        bidirectional=bidirectional,
        is_accessible=accessible,
    )
    session.add(edge)
    session.flush()
    return edge


def get_location(session: Session, location_id: int) -> Location | None:
    return session.get(Location, location_id)


def list_locations(session: Session) -> list[Location]:
    return list(session.scalars(select(Location).order_by(Location.id)))


def list_objects_in(session: Session, location_id: int) -> list[GameObject]:
    return list(
        session.scalars(
            select(GameObject).where(GameObject.location_id == location_id).order_by(GameObject.id)
        )
    )


def iter_children(session: Session, location_id: int) -> Iterable[Location]:
    return iter(
        session.scalars(
            select(Location).where(Location.parent_id == location_id).order_by(Location.id)
        )
    )


def update_dynamic_attribute(
    session: Session,
    location_id: int,
    attribute: str,
    *,
    delta: float = 0.0,
    clamp: tuple[float, float] | None = None,
) -> float:
    """Modifica un attributo dinamico di una Location e ritorna il nuovo valore.

    Supporta: `cleanliness_level`, `noise_level`, `safety_rating`, `aesthetic_score`
    (float 0..1) e `crowd_level` (int). Le modifiche sono additive.
    """
    loc = get_location(session, location_id)
    if loc is None:
        raise LookupError(f"Location id={location_id} non trovata")

    allowed = {
        "cleanliness_level",
        "noise_level",
        "safety_rating",
        "aesthetic_score",
        "crowd_level",
    }
    if attribute not in allowed:
        raise ValueError(
            f"attributo '{attribute}' non modificabile (consentiti: {sorted(allowed)})"
        )

    new_value = getattr(loc, attribute) + delta
    if clamp is not None:
        lo, hi = clamp
        new_value = max(lo, min(hi, new_value))
    setattr(loc, attribute, new_value)
    session.flush()
    return float(new_value)
