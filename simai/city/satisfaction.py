"""SatisfactionService — soddisfazione dei cittadini verso la città.

Combina la copertura dei servizi pubblici in un punteggio [0, 1] per
ogni area e un overall pesato. Non tocca il mood degli NPC (rimandato
a 4.7b).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from sqlalchemy.orm import Session

from simai.city.enums import PublicServiceType
from simai.city.service import CityService
from simai.world.district import District

#: Pesi delle aree nel punteggio overall.
SATISFACTION_WEIGHTS: Final[dict[str, float]] = {
    "safety": 0.20,
    "health": 0.18,
    "education": 0.18,
    "cleanliness": 0.17,
    "wellbeing": 0.15,
    "infrastructure": 0.12,
}

#: Mappa servizio → area di soddisfazione.
SERVICE_TO_AREA: Final[dict[PublicServiceType, str]] = {
    PublicServiceType.POLICE: "safety",
    PublicServiceType.FIRE: "safety",
    PublicServiceType.HOSPITAL: "health",
    PublicServiceType.SCHOOL: "education",
    PublicServiceType.GARBAGE: "cleanliness",
    PublicServiceType.PARK: "wellbeing",
}


@dataclass(frozen=True, slots=True)
class DistrictSatisfaction:
    district_id: int
    district_name: str
    safety: float
    health: float
    education: float
    cleanliness: float
    wellbeing: float
    infrastructure: float
    overall: float

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "district_id": self.district_id,
            "district_name": self.district_name,
            "safety": self.safety,
            "health": self.health,
            "education": self.education,
            "cleanliness": self.cleanliness,
            "wellbeing": self.wellbeing,
            "infrastructure": self.infrastructure,
            "overall": self.overall,
        }


@dataclass(slots=True)
class CitySatisfactionReport:
    districts: list[DistrictSatisfaction] = field(default_factory=list)

    @property
    def overall(self) -> float:
        if not self.districts:
            return 0.0
        return sum(d.overall for d in self.districts) / len(self.districts)


class SatisfactionService:
    """Servizio stateless di soddisfazione."""

    @staticmethod
    def compute_district(session: Session, district: District) -> DistrictSatisfaction:
        """Punteggio soddisfazione per un singolo quartiere."""
        from simai.city.infrastructure.service import InfrastructureService

        services = CityService.services_of_district(session, district.id)
        area_sums: dict[str, list[float]] = {k: [] for k in SATISFACTION_WEIGHTS}
        for svc in services:
            try:
                t = PublicServiceType(svc.type)
            except ValueError:
                continue
            area = SERVICE_TO_AREA.get(t)
            if area is None or area not in area_sums:
                continue
            area_sums[area].append(float(svc.quality))

        def avg(xs: list[float]) -> float:
            return sum(xs) / len(xs) if xs else 0.0

        safety = avg(area_sums["safety"])
        health = avg(area_sums["health"])
        education = avg(area_sums["education"])
        cleanliness = avg(area_sums["cleanliness"])
        wellbeing = avg(area_sums["wellbeing"])

        # Infrastructure: media di road coverage + lighting coverage
        road_cov = InfrastructureService.district_roads_coverage(session, district)
        light_cov = InfrastructureService.district_lighting_coverage(session, district)
        infrastructure = (road_cov + light_cov) / 2.0

        # Safety extra bonus da illuminazione (fino a +0.10)
        safety = min(1.0, safety + light_cov * 0.10)

        overall = (
            SATISFACTION_WEIGHTS["safety"] * safety
            + SATISFACTION_WEIGHTS["health"] * health
            + SATISFACTION_WEIGHTS["education"] * education
            + SATISFACTION_WEIGHTS["cleanliness"] * cleanliness
            + SATISFACTION_WEIGHTS["wellbeing"] * wellbeing
            + SATISFACTION_WEIGHTS["infrastructure"] * infrastructure
        )

        return DistrictSatisfaction(
            district_id=district.id,
            district_name=district.name,
            safety=round(safety, 3),
            health=round(health, 3),
            education=round(education, 3),
            cleanliness=round(cleanliness, 3),
            wellbeing=round(wellbeing, 3),
            infrastructure=round(infrastructure, 3),
            overall=round(overall, 3),
        )

    @staticmethod
    def compute_all(session: Session) -> CitySatisfactionReport:
        """Ritorna la soddisfazione per tutti i quartieri."""
        from sqlalchemy import select

        districts = list(session.scalars(select(District).order_by(District.id)))
        return CitySatisfactionReport(
            districts=[SatisfactionService.compute_district(session, d) for d in districts]
        )


__all__ = [
    "SATISFACTION_WEIGHTS",
    "SERVICE_TO_AREA",
    "CitySatisfactionReport",
    "DistrictSatisfaction",
    "SatisfactionService",
]
