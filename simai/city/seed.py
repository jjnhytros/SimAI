"""Seed di servizi pubblici demo."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.enums import PublicServiceType
from simai.city.models import PublicService
from simai.city.service import CityService


def seed_demo_city(session: Session) -> int:
    """Registra i servizi demo per il primo quartiere. Ritorna il numero creati."""
    from simai.world.district import District

    existing = session.scalars(select(PublicService)).first()
    if existing is not None:
        return 0

    districts = list(session.scalars(select(District).order_by(District.id)))
    if not districts:
        return 0

    center = districts[0]
    created = 0
    # Registra 5 servizi con qualità diverse
    services: list[tuple[PublicServiceType, float, int | None]] = [
        (PublicServiceType.POLICE, 0.65, 40),
        (PublicServiceType.HOSPITAL, 0.55, 50),
        (PublicServiceType.SCHOOL, 0.70, 35),
        (PublicServiceType.GARBAGE, 0.50, 25),
        (PublicServiceType.PARK, 0.80, 5),
    ]
    for t, quality, cost in services:
        CityService.register_service(
            session,
            district_id=center.id,
            type_=t,
            quality=quality,
            daily_cost=cost,
        )
        created += 1
    return created


__all__ = ["seed_demo_city"]
