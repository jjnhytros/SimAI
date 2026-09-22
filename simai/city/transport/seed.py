"""Seed di linee pubbliche demo."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.transport.enums import RouteType
from simai.city.transport.models import TransportRoute
from simai.city.transport.service import TransportService
from simai.world.enums import LocationType
from simai.world.models import Location


def seed_demo_routes(session: Session) -> int:
    """Crea 2 linee demo (bus + metro) tra le location principali.

    Ritorna il numero di linee create.
    """
    existing = session.scalars(select(TransportRoute)).first()
    if existing is not None:
        return 0

    # Trova location utili
    locations = list(session.scalars(select(Location).order_by(Location.id)))
    if len(locations) < 4:
        return 0

    # Prendi alcune location come fermate: casa, 2 negozi, 1 altra
    stops: list[int] = []
    for loc in locations:
        if loc.type in (
            LocationType.BUILDING.value,
            LocationType.SHOP.value,
            LocationType.OUTDOOR.value,
        ):
            stops.append(loc.id)
        if len(stops) >= 5:
            break
    if len(stops) < 2:
        return 0

    # Bus: collega tutte le stop in sequenza
    TransportService.create_route(
        session,
        name="Linea Bus 1",
        route_type=RouteType.BUS,
        stop_location_ids=stops,
    )

    # Metro: solo le prime 3 stop (più "veloce" e "mirata")
    if len(stops) >= 3:
        TransportService.create_route(
            session,
            name="Linea Metro A",
            route_type=RouteType.METRO,
            stop_location_ids=stops[:3],
        )
    return 2


__all__ = ["seed_demo_routes"]
