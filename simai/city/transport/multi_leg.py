"""Multi-leg travel: composizione di più tratte (walk + bus + walk, ecc.)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from sqlalchemy.orm import Session

from simai.city.transport.enums import (
    BUS_WAIT_TICKS,
    CAR_FUEL_COST_PER_CELL,
    CAR_FUEL_PER_CELL,
    CAR_SPEED,
    METRO_WAIT_TICKS,
    WALK_SPEED,
    RouteType,
    TransportMode,
    VehicleType,
)
from simai.city.transport.models import RouteStop, TransportRoute
from simai.npc.models import Character
from simai.utils import (
    coerce_float,
    coerce_int,
    coerce_optional_int,
    coerce_str,
)
from simai.world.models import Location

#: Distanza massima (in celle) che si è disposti a camminare per una fermata.
MAX_WALK_TO_STOP: Final[float] = 25.0

#: Distanza massima totale (in celle) di walk complessivo in un piano multi-leg.
MAX_TOTAL_WALK: Final[float] = 50.0

#: Penalità di trasferimento (in tick) per ogni cambio di mezzo.
TRANSFER_PENALTY_TICKS: Final[int] = 3


@dataclass(frozen=True, slots=True)
class TravelLeg:
    """Una singola tratta di un viaggio."""

    mode: TransportMode
    from_location_id: int
    to_location_id: int
    duration_ticks: int
    cost: int
    fuel_needed: float = 0.0
    route_id: int | None = None
    description: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode.value,
            "from_location_id": self.from_location_id,
            "to_location_id": self.to_location_id,
            "duration_ticks": self.duration_ticks,
            "cost": self.cost,
            "fuel_needed": self.fuel_needed,
            "route_id": self.route_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TravelLeg:
        return cls(
            mode=TransportMode(coerce_str(data["mode"], name="leg.mode")),
            from_location_id=coerce_int(data["from_location_id"], name="leg.from_location_id"),
            to_location_id=coerce_int(data["to_location_id"], name="leg.to_location_id"),
            duration_ticks=coerce_int(data["duration_ticks"], name="leg.duration_ticks"),
            cost=coerce_int(data["cost"], name="leg.cost"),
            fuel_needed=coerce_float(data.get("fuel_needed", 0.0), name="leg.fuel_needed"),
            route_id=coerce_optional_int(data.get("route_id"), name="leg.route_id"),
            description=coerce_str(data.get("description", ""), name="leg.description"),
        )


@dataclass(frozen=True, slots=True)
class MultiLegPlan:
    """Piano multi-tratta: sequenza di `TravelLeg`."""

    legs: tuple[TravelLeg, ...]

    @property
    def total_ticks(self) -> int:
        return sum(leg.duration_ticks for leg in self.legs)

    @property
    def total_cost(self) -> int:
        return sum(leg.cost for leg in self.legs)

    @property
    def total_fuel(self) -> float:
        return sum(leg.fuel_needed for leg in self.legs)

    @property
    def from_location_id(self) -> int:
        return self.legs[0].from_location_id if self.legs else 0

    @property
    def to_location_id(self) -> int:
        return self.legs[-1].to_location_id if self.legs else 0

    @property
    def mode_label(self) -> str:
        """Es. `WALK`, `WALK+BUS+WALK`, `CAR`, ecc."""
        if not self.legs:
            return "NONE"
        # Compatta i walk consecutivi
        return "+".join(leg.mode.value for leg in self.legs)

    @property
    def description(self) -> str:
        return " → ".join(leg.description for leg in self.legs if leg.description)

    @classmethod
    def from_single(cls, plan: object) -> MultiLegPlan:
        """Wrapper per un singolo TravelPlan (retro-compatibilità)."""
        from simai.city.transport.service import TravelPlan

        if not isinstance(plan, TravelPlan):
            raise TypeError("plan deve essere un TravelPlan")
        return cls(
            legs=(
                TravelLeg(
                    mode=plan.mode,
                    from_location_id=plan.from_location_id,
                    to_location_id=plan.to_location_id,
                    duration_ticks=plan.duration_ticks,
                    cost=plan.cost,
                    fuel_needed=plan.fuel_needed,
                    route_id=plan.route_id,
                    description=plan.description,
                ),
            )
        )


class MultiLegPlanner:
    """Costruisce piani multi-tratta."""

    @staticmethod
    def _distance(session: Session, from_id: int, to_id: int) -> float:
        """Distanza geometrica tra due Location."""
        if from_id == to_id:
            return 0.0
        a = session.get(Location, from_id)
        b = session.get(Location, to_id)
        if a is None or b is None:
            return 0.0
        ax, ay = a.center()
        bx, by = b.center()
        return math.hypot(ax - bx, ay - by)

    @staticmethod
    def plan_all(
        session: Session,
        character: Character,
        *,
        from_location_id: int,
        to_location_id: int,
    ) -> list[MultiLegPlan]:
        """Ritorna i migliori piani (1 leg + multi-leg)."""
        if from_location_id == to_location_id:
            return [
                MultiLegPlan(
                    legs=(
                        TravelLeg(
                            mode=TransportMode.WALK,
                            from_location_id=from_location_id,
                            to_location_id=to_location_id,
                            duration_ticks=0,
                            cost=0,
                            description="già sul posto",
                        ),
                    )
                )
            ]

        plans: list[MultiLegPlan] = []

        # 1. Walk-only sempre disponibile
        base_dist = MultiLegPlanner._distance(session, from_location_id, to_location_id)
        if base_dist > 0:
            plans.append(
                MultiLegPlanner._walk_leg(
                    from_id=from_location_id,
                    to_id=to_location_id,
                    distance=base_dist,
                )
            )

        # 2. Auto / Bici (single leg)
        car = MultiLegPlanner._vehicle_leg(
            session,
            character,
            from_id=from_location_id,
            to_id=to_location_id,
            distance=base_dist,
        )
        if car is not None:
            plans.append(car)

        # 3. Walk + Bus/Metro + Walk (per ogni route)
        routes = list(
            session.scalars(
                # solo route attive
                __import__("sqlalchemy")
                .select(TransportRoute)
                .where(TransportRoute.is_active.is_(True))
            )
        )
        for route in routes:
            plans.extend(
                MultiLegPlanner._route_combo_plans(
                    session,
                    route,
                    from_id=from_location_id,
                    to_id=to_location_id,
                )
            )

        # Deduplica (per composizione mode + from + to)
        seen: set[tuple[object, ...]] = set()
        unique: list[MultiLegPlan] = []
        for p in plans:
            key = (
                p.mode_label,
                p.from_location_id,
                p.to_location_id,
                tuple(leg.route_id for leg in p.legs),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(p)

        # Ordina per (total_ticks, total_cost)
        unique.sort(key=lambda p: (p.total_ticks, p.total_cost))
        return unique[:20]  # cap per UI

    # ------------------------------------------------------------------
    # Leg builders
    # ------------------------------------------------------------------

    @staticmethod
    def _walk_leg(*, from_id: int, to_id: int, distance: float) -> MultiLegPlan:
        return MultiLegPlan(
            legs=(
                TravelLeg(
                    mode=TransportMode.WALK,
                    from_location_id=from_id,
                    to_location_id=to_id,
                    duration_ticks=max(1, int(distance / WALK_SPEED)),
                    cost=0,
                    description=f"a piedi ({distance:.1f} celle)",
                ),
            )
        )

    @staticmethod
    def _vehicle_leg(
        session: Session,
        character: Character,
        *,
        from_id: int,
        to_id: int,
        distance: float,
    ) -> MultiLegPlan | None:
        """Piano in auto o bici (single leg)."""
        from simai.city.transport.service import TransportService

        bike = TransportService.vehicle_of(session, character.id, VehicleType.BIKE)
        car = TransportService.vehicle_of(session, character.id, VehicleType.CAR)

        # Priorità: auto se disponibile + ha carburante, altrimenti bici
        if car is not None and car.condition > 0.2:
            fuel_needed = distance * CAR_FUEL_PER_CELL
            if car.fuel >= fuel_needed:
                return MultiLegPlan(
                    legs=(
                        TravelLeg(
                            mode=TransportMode.CAR,
                            from_location_id=from_id,
                            to_location_id=to_id,
                            duration_ticks=max(1, int(distance / CAR_SPEED)),
                            cost=int(distance * CAR_FUEL_COST_PER_CELL),
                            fuel_needed=fuel_needed,
                            description=f"in auto ({distance:.1f} celle)",
                        ),
                    )
                )
        if bike is not None and bike.condition > 0.2:
            return MultiLegPlan(
                legs=(
                    TravelLeg(
                        mode=TransportMode.BIKE,
                        from_location_id=from_id,
                        to_location_id=to_id,
                        duration_ticks=max(1, int(distance / 1.9)),
                        cost=0,
                        description=f"in bici ({distance:.1f} celle)",
                    ),
                )
            )
        return None

    @staticmethod
    def _route_combo_plans(
        session: Session,
        route: TransportRoute,
        *,
        from_id: int,
        to_id: int,
    ) -> list[MultiLegPlan]:
        """Genera i piani `[walk, route, walk]` per una linea."""
        stops = list(
            session.scalars(
                __import__("sqlalchemy")
                .select(RouteStop)
                .where(RouteStop.route_id == route.id)
                .order_by(RouteStop.sequence)
            )
        )
        if len(stops) < 2:
            return []

        is_bus = route.route_type == RouteType.BUS.value
        route_mode = TransportMode.BUS if is_bus else TransportMode.METRO
        route_speed = route.speed_cells_per_tick
        wait_ticks = BUS_WAIT_TICKS if is_bus else METRO_WAIT_TICKS

        plans: list[MultiLegPlan] = []
        for board in stops:
            walk1_dist = MultiLegPlanner._distance(session, from_id, board.location_id)
            if walk1_dist <= 0.0:
                # Se già su un stop, walk1 è zero (opzionale)
                walk1_dist = 0.0
            if walk1_dist > MAX_WALK_TO_STOP:
                continue

            for alight in stops:
                if alight.location_id == board.location_id:
                    continue
                ride_dist = MultiLegPlanner._distance(
                    session, board.location_id, alight.location_id
                )
                if ride_dist <= 0.0:
                    continue
                walk2_dist = MultiLegPlanner._distance(session, alight.location_id, to_id)
                if walk2_dist > MAX_WALK_TO_STOP:
                    continue
                if walk1_dist + walk2_dist > MAX_TOTAL_WALK:
                    continue

                legs: list[TravelLeg] = []
                if walk1_dist > 0.5:
                    legs.append(
                        TravelLeg(
                            mode=TransportMode.WALK,
                            from_location_id=from_id,
                            to_location_id=board.location_id,
                            duration_ticks=max(1, int(walk1_dist / WALK_SPEED)),
                            cost=0,
                            description=f"a piedi → stop ({walk1_dist:.1f})",
                        )
                    )
                legs.append(
                    TravelLeg(
                        mode=route_mode,
                        from_location_id=board.location_id,
                        to_location_id=alight.location_id,
                        duration_ticks=(
                            wait_ticks
                            + TRANSFER_PENALTY_TICKS
                            + max(1, int(ride_dist / route_speed))
                        ),
                        cost=route.base_fare,
                        route_id=route.id,
                        description=(f"{route.name} ({ride_dist:.1f} celle)"),
                    )
                )
                if walk2_dist > 0.5:
                    legs.append(
                        TravelLeg(
                            mode=TransportMode.WALK,
                            from_location_id=alight.location_id,
                            to_location_id=to_id,
                            duration_ticks=max(1, int(walk2_dist / WALK_SPEED)),
                            cost=0,
                            description=f"a piedi ({walk2_dist:.1f})",
                        )
                    )
                plans.append(MultiLegPlan(legs=tuple(legs)))
        return plans


__all__ = [
    "MAX_TOTAL_WALK",
    "MAX_WALK_TO_STOP",
    "TRANSFER_PENALTY_TICKS",
    "MultiLegPlan",
    "MultiLegPlanner",
    "TravelLeg",
]
