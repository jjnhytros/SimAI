"""InfrastructureService — strade, lampioni, copertura, degrado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from simai.city.infrastructure.enums import (
    LIGHT_COSTS,
    LIGHT_DAILY_DEGRADATION,
    LIGHT_OFF_CONDITION,
    LIGHT_RADII,
    ROAD_COSTS,
    ROAD_DAILY_DEGRADATION,
    LightType,
    RoadType,
)
from simai.city.infrastructure.models import RoadTile, StreetLight
from simai.economy.ledger import JournalEntryKind
from simai.world.district import District

if TYPE_CHECKING:
    from simai.core.anthalys_datetime import AnthalysDateTime
    from simai.npc.models import Character


#: Raggio massimo consentito per un lampione.
MAX_LIGHT_RADIUS: int = 10

#: Coordinata massima consentita (griglia pratica).
MAX_COORD: int = 199


class InfrastructureError(Exception):
    """Errore di validazione infrastruttura."""


@dataclass(frozen=True, slots=True)
class PlaceResult:
    ok: bool
    reason: str
    cost_paid: int = 0


@dataclass(slots=True)
class InfrastructureTickReport:
    roads_degraded: int = 0
    lights_degraded: int = 0
    lights_turned_off: int = 0


class InfrastructureService:
    """Servizio stateless di infrastrutture civiche."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def roads_in_bbox(
        session: Session,
        *,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
    ) -> list[RoadTile]:
        return list(
            session.scalars(
                select(RoadTile).where(
                    RoadTile.x >= x0,
                    RoadTile.x <= x1,
                    RoadTile.y >= y0,
                    RoadTile.y <= y1,
                )
            )
        )

    @staticmethod
    def lights_in_bbox(
        session: Session,
        *,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
    ) -> list[StreetLight]:
        return list(
            session.scalars(
                select(StreetLight).where(
                    StreetLight.x >= x0,
                    StreetLight.x <= x1,
                    StreetLight.y >= y0,
                    StreetLight.y <= y1,
                )
            )
        )

    @staticmethod
    def get_road(session: Session, *, x: int, y: int) -> RoadTile | None:
        return session.scalars(select(RoadTile).where(RoadTile.x == x, RoadTile.y == y)).first()

    @staticmethod
    def get_light(session: Session, *, x: int, y: int) -> StreetLight | None:
        return session.scalars(
            select(StreetLight).where(StreetLight.x == x, StreetLight.y == y)
        ).first()

    # ------------------------------------------------------------------
    # District resolution
    # ------------------------------------------------------------------

    @staticmethod
    def district_at(session: Session, *, x: int, y: int) -> District | None:
        """Ritorna il District che contiene (x, y), o ``None``."""
        districts = list(session.scalars(select(District)))
        for d in districts:
            if (
                d.bounds_x <= x < d.bounds_x + d.bounds_w
                and d.bounds_y <= y < d.bounds_y + d.bounds_h
            ):
                return d
        return None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_coords(x: int, y: int) -> None:
        if not (0 <= x <= MAX_COORD and 0 <= y <= MAX_COORD):
            raise InfrastructureError(f"coordinate ({x},{y}) fuori range [0, {MAX_COORD}]")

    # ------------------------------------------------------------------
    # Place road
    # ------------------------------------------------------------------

    @staticmethod
    def place_road(
        session: Session,
        *,
        x: int,
        y: int,
        road_type: RoadType = RoadType.STREET,
        buyer: Character | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> PlaceResult:
        InfrastructureService._validate_coords(x, y)

        existing = InfrastructureService.get_road(session, x=x, y=y)
        if existing is not None:
            # Aggiorna tipo + condizione
            existing.road_type = road_type.value
            existing.condition = 1.0
            session.flush()
            return PlaceResult(True, "updated", 0)

        cost = ROAD_COSTS.get(road_type, 20)

        if buyer is not None:
            if int(buyer.athel_balance) < cost:
                return PlaceResult(
                    False,
                    f"fondi insufficienti: {buyer.athel_balance} < {cost}",
                )
            from simai.npc.economy.service import WealthService

            WealthService.add(
                session,
                buyer,
                -cost,
                current_dt=current_dt,
                kind=JournalEntryKind.PURCHASE,
                description=f"Posa strada {road_type.value} @ ({x},{y})",
                reference_type="infrastructure",
                metadata={"road_type": road_type.value, "x": x, "y": y},
            )

        district = InfrastructureService.district_at(session, x=x, y=y)
        now_secs = current_dt.to_total_seconds() if current_dt else 0

        session.add(
            RoadTile(
                x=x,
                y=y,
                road_type=road_type.value,
                condition=1.0,
                district_id=district.id if district else None,
                applied_at_total_seconds=now_secs,
                metadata_json={},
            )
        )
        session.flush()
        return PlaceResult(True, "ok", cost)

    @staticmethod
    def remove_road(session: Session, *, x: int, y: int) -> bool:
        road = InfrastructureService.get_road(session, x=x, y=y)
        if road is None:
            return False
        session.delete(road)
        session.flush()
        return True

    # ------------------------------------------------------------------
    # Place light
    # ------------------------------------------------------------------

    @staticmethod
    def place_light(
        session: Session,
        *,
        x: int,
        y: int,
        light_type: LightType = LightType.STANDARD,
        buyer: Character | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> PlaceResult:
        InfrastructureService._validate_coords(x, y)

        existing = InfrastructureService.get_light(session, x=x, y=y)
        if existing is not None:
            # Reinstalla
            existing.light_type = light_type.value
            existing.radius = LIGHT_RADII.get(light_type, 3)
            existing.condition = 1.0
            existing.is_active = True
            session.flush()
            return PlaceResult(True, "updated", 0)

        cost = LIGHT_COSTS.get(light_type, 30)

        if buyer is not None:
            if int(buyer.athel_balance) < cost:
                return PlaceResult(
                    False,
                    f"fondi insufficienti: {buyer.athel_balance} < {cost}",
                )
            from simai.npc.economy.service import WealthService

            WealthService.add(
                session,
                buyer,
                -cost,
                current_dt=current_dt,
                kind=JournalEntryKind.PURCHASE,
                description=f"Posa lampione {light_type.value} @ ({x},{y})",
                reference_type="infrastructure",
                metadata={"light_type": light_type.value, "x": x, "y": y},
            )

        district = InfrastructureService.district_at(session, x=x, y=y)
        now_secs = current_dt.to_total_seconds() if current_dt else 0
        radius = LIGHT_RADII.get(light_type, 3)

        session.add(
            StreetLight(
                x=x,
                y=y,
                light_type=light_type.value,
                radius=radius,
                condition=1.0,
                is_active=True,
                district_id=district.id if district else None,
                applied_at_total_seconds=now_secs,
                metadata_json={},
            )
        )
        session.flush()
        return PlaceResult(True, "ok", cost)

    @staticmethod
    def remove_light(session: Session, *, x: int, y: int) -> bool:
        light = InfrastructureService.get_light(session, x=x, y=y)
        if light is None:
            return False
        session.delete(light)
        session.flush()
        return True

    # ------------------------------------------------------------------
    # Coverage
    # ------------------------------------------------------------------

    @staticmethod
    def lighting_coverage_at(session: Session, *, x: int, y: int) -> float:
        """Copertura luminosa [0, 1] della cella (x, y).

        Somma le condizioni dei lampioni attivi entro il loro raggio,
        clampata a 1.0.
        """
        lights = list(session.scalars(select(StreetLight).where(StreetLight.is_active.is_(True))))
        total = 0.0
        for light in lights:
            dx = light.x - x
            dy = light.y - y
            if dx * dx + dy * dy <= light.radius * light.radius:
                total += light.condition
        return min(1.0, total)

    @staticmethod
    def district_lighting_coverage(session: Session, district: District) -> float:
        """Copertura luminosa media in un distretto [0, 1]."""
        x0 = district.bounds_x
        y0 = district.bounds_y
        x1 = district.bounds_x + district.bounds_w - 1
        y1 = district.bounds_y + district.bounds_h - 1

        lights = InfrastructureService.lights_in_bbox(session, x0=x0, y0=y0, x1=x1, y1=y1)
        active = [light for light in lights if light.is_active]
        if not active:
            return 0.0

        # Coverage = min(1, SUM(condition) / (area / 400))
        area = district.bounds_w * district.bounds_h
        expected = max(1, area // 400)
        total = sum(light.condition for light in active)
        return min(1.0, total / expected)

    @staticmethod
    def district_roads_coverage(session: Session, district: District) -> float:
        """Copertura stradale media [0, 1] (condition media delle strade)."""
        x0 = district.bounds_x
        y0 = district.bounds_y
        x1 = district.bounds_x + district.bounds_w - 1
        y1 = district.bounds_y + district.bounds_h - 1

        roads = InfrastructureService.roads_in_bbox(session, x0=x0, y0=y0, x1=x1, y1=y1)
        if not roads:
            return 0.0
        total = sum(r.condition for r in roads)
        return min(1.0, total / len(roads))

    # ------------------------------------------------------------------
    # Daily tick
    # ------------------------------------------------------------------

    @staticmethod
    def daily_tick(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
    ) -> InfrastructureTickReport:
        """Degrada condition di strade e lampioni. Spegne i lampioni troppo rovinati."""
        report = InfrastructureTickReport()

        roads = list(session.scalars(select(RoadTile)))
        for r in roads:
            r.condition = max(0.0, r.condition - ROAD_DAILY_DEGRADATION)
            report.roads_degraded += 1

        lights = list(session.scalars(select(StreetLight)))
        for light in lights:
            light.condition = max(0.0, light.condition - LIGHT_DAILY_DEGRADATION)
            report.lights_degraded += 1
            if light.is_active and light.condition < LIGHT_OFF_CONDITION:
                light.is_active = False
                report.lights_turned_off += 1
                logger.info(
                    "Lampione spento per condizione: id={} (cond={:.2f})",
                    light.id,
                    light.condition,
                )

        session.flush()
        return report

    # ------------------------------------------------------------------
    # Bulk
    # ------------------------------------------------------------------

    @staticmethod
    def clear_all(session: Session) -> tuple[int, int]:
        """Rimuove tutte le strade e i lampioni. Ritorna (n_roads, n_lights)."""
        n_roads = int(session.scalar(select(func.count()).select_from(RoadTile)) or 0)
        n_lights = int(session.scalar(select(func.count()).select_from(StreetLight)) or 0)
        session.execute(delete(RoadTile))
        session.execute(delete(StreetLight))
        session.flush()
        return n_roads, n_lights


__all__ = [
    "MAX_COORD",
    "MAX_LIGHT_RADIUS",
    "InfrastructureError",
    "InfrastructureService",
    "InfrastructureTickReport",
    "PlaceResult",
]
