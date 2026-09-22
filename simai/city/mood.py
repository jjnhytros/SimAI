"""CityMoodService — moodlet quotidiani ai cittadini in base ai servizi."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.satisfaction import SatisfactionService
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.models import Character
from simai.npc.mood import Moodlet, MoodState
from simai.npc.needs.needs import Needs
from simai.world.district import District
from simai.world.lot import Lot
from simai.world.models import Location

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

#: Durata del moodlet (1 giorno Anthalys = 336 tick).
CITY_MOODLET_DURATION: Final[int] = 336

#: Soglie overall.
EXCELLENT_THRESHOLD: Final[float] = 0.75
GOOD_THRESHOLD: Final[float] = 0.50
POOR_THRESHOLD: Final[float] = 0.30
CRITICAL_THRESHOLD: Final[float] = 0.15

#: Soglia per "servizio carente" in una singola area.
AREA_POOR_THRESHOLD: Final[float] = 0.30

#: Delta happiness per moodlet.
MOOD_EXCELLENT: Final[float] = +0.06
MOOD_GOOD: Final[float] = +0.02
MOOD_POOR: Final[float] = -0.06
MOOD_CRITICAL: Final[float] = -0.12
MOOD_AREA_POOR: Final[float] = -0.04


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class CityMoodReport:
    """Esito di un tick di moodlet città."""

    citizens_processed: int = 0
    moodlets_applied: int = 0
    districts_evaluated: int = 0
    district_overall: dict[int, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class CityMoodService:
    """Servizio stateless di moodlet città."""

    # ------------------------------------------------------------------
    # District resolution
    # ------------------------------------------------------------------

    @staticmethod
    def district_of_character(session: Session, character: Character) -> District | None:
        """Ritorna il District in cui si trova il character, o il primo.

        Logica:
          1. Risale dal `location_id` alla Location radice (BUILDING/SHOP).
          2. Trova il Lot che ha `location_id` = radice.
          3. Ritorna il `district_id` del Lot.
          4. Fallback: primo District per id.
        """
        if character.location_id is not None:
            root = CityMoodService._root_location(session, character.location_id)
            if root is not None:
                lot = session.scalars(select(Lot).where(Lot.location_id == root.id)).first()
                if lot is not None:
                    return session.get(District, lot.district_id)

        # Fallback: primo district
        return session.scalars(select(District).order_by(District.id)).first()

    @staticmethod
    def _root_location(session: Session, location_id: int) -> Location | None:
        current = session.get(Location, location_id)
        if current is None:
            return None
        # Sale fino alla radice (no parent)
        guard = 0
        while current.parent_id is not None and guard < 20:
            parent = session.get(Location, current.parent_id)
            if parent is None:
                break
            current = parent
            guard += 1
        return current

    # ------------------------------------------------------------------
    # Daily tick
    # ------------------------------------------------------------------

    @staticmethod
    def daily_tick(
        session: Session,
        characters: list[Character],
        *,
        current_dt: AnthalysDateTime,
    ) -> CityMoodReport:
        """Applica moodlet quotidiani a tutti i character vivi con location.

        Calcola la soddisfazione una sola volta per distretto, poi la
        applica a tutti i cittadini di quel distretto.
        """
        report = CityMoodReport()

        # 1. Cache soddisfazione per distretto
        satisfaction_cache: dict[int, dict[str, float]] = {}
        districts = list(session.scalars(select(District).order_by(District.id)))
        for d in districts:
            ds = SatisfactionService.compute_district(session, d)
            satisfaction_cache[d.id] = {
                "overall": ds.overall,
                "safety": ds.safety,
                "health": ds.health,
                "education": ds.education,
                "cleanliness": ds.cleanliness,
                "wellbeing": ds.wellbeing,
            }
            report.district_overall[d.id] = ds.overall
        report.districts_evaluated = len(districts)

        if not satisfaction_cache:
            return report

        # 2. Applica moodlet per character
        for c in characters:
            if not c.is_alive or c.location_id is None:
                continue
            report.citizens_processed += 1

            district = CityMoodService.district_of_character(session, c)
            if district is None:
                continue
            stats = satisfaction_cache.get(district.id)
            if stats is None:
                continue

            moodlets = CityMoodService._compute_moodlets(district.id, stats)
            if not moodlets:
                continue

            CityMoodService._apply_moodlets(c, moodlets)
            report.moodlets_applied += len(moodlets)

        session.flush()
        return report

    # ------------------------------------------------------------------
    # Moodlet computation
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_moodlets(district_id: int, stats: dict[str, float]) -> list[Moodlet]:
        """Genera la lista di moodlet per un distretto."""
        moodlets: list[Moodlet] = []
        overall = stats.get("overall", 0.0)

        # Overall
        if overall >= EXCELLENT_THRESHOLD:
            moodlets.append(
                Moodlet(
                    name="Servizi eccellenti",
                    remaining_ticks=CITY_MOODLET_DURATION,
                    happiness_delta=MOOD_EXCELLENT,
                    source=f"city_overall_{district_id}",
                )
            )
        elif overall >= GOOD_THRESHOLD:
            moodlets.append(
                Moodlet(
                    name="Servizi buoni",
                    remaining_ticks=CITY_MOODLET_DURATION,
                    happiness_delta=MOOD_GOOD,
                    source=f"city_overall_{district_id}",
                )
            )
        elif overall < CRITICAL_THRESHOLD:
            moodlets.append(
                Moodlet(
                    name="Servizi in rovina",
                    remaining_ticks=CITY_MOODLET_DURATION,
                    happiness_delta=MOOD_CRITICAL,
                    source=f"city_overall_{district_id}",
                )
            )
        elif overall < POOR_THRESHOLD:
            moodlets.append(
                Moodlet(
                    name="Servizi scadenti",
                    remaining_ticks=CITY_MOODLET_DURATION,
                    happiness_delta=MOOD_POOR,
                    source=f"city_overall_{district_id}",
                )
            )

        # Aree specifiche (solo se sotto soglia)
        area_labels = {
            "safety": "Insicurezza",
            "health": "Sanità carente",
            "education": "Scuole scadenti",
            "cleanliness": "Città sporca",
            "wellbeing": "Poco benessere",
        }
        for area, label in area_labels.items():
            v = stats.get(area, 0.0)
            if v < AREA_POOR_THRESHOLD:
                moodlets.append(
                    Moodlet(
                        name=label,
                        remaining_ticks=CITY_MOODLET_DURATION,
                        happiness_delta=MOOD_AREA_POOR,
                        source=f"city_{area}_{district_id}",
                    )
                )

        return moodlets

    # ------------------------------------------------------------------
    # Moodlet application
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_moodlets(character: Character, moodlets: list[Moodlet]) -> None:
        """Applica i moodlet al Character (aggiorna `mood_json`)."""
        mood = MoodState.from_dict(character.mood_json or {})
        needs = Needs.from_dict(character.needs_json or {})
        new_mood = mood.tick(needs, tuple(moodlets))
        character.mood_json = new_mood.to_dict()


__all__ = [
    "AREA_POOR_THRESHOLD",
    "CITY_MOODLET_DURATION",
    "CRITICAL_THRESHOLD",
    "EXCELLENT_THRESHOLD",
    "GOOD_THRESHOLD",
    "MOOD_AREA_POOR",
    "MOOD_CRITICAL",
    "MOOD_EXCELLENT",
    "MOOD_GOOD",
    "MOOD_POOR",
    "POOR_THRESHOLD",
    "CityMoodReport",
    "CityMoodService",
]
