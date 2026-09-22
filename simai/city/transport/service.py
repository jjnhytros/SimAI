"""TransportService — pathfinding multi-modale, veicoli, linee."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.transport.enums import (
    BIKE_SPEED,
    BUS_FARE,
    BUS_SPEED,
    BUS_WAIT_TICKS,
    CAR_FUEL_COST_PER_CELL,
    CAR_FUEL_PER_CELL,
    CAR_SPEED,
    MAX_AI_TRIPS_PER_DAY,
    METRO_FARE,
    METRO_SPEED,
    METRO_WAIT_TICKS,
    MIN_WALK_DISTANCE_ALWAYS,
    VEHICLE_PRICES,
    WALK_SPEED,
    RouteType,
    TransportMode,
    VehicleType,
)
from simai.city.transport.models import RouteStop, TransportRoute, Vehicle
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.jobs import JobService
from simai.economy.ledger import JournalEntryKind
from simai.npc.economy.service import EconomyError, WealthService
from simai.npc.models import Character
from simai.world.district import District
from simai.world.lot import Lot
from simai.world.models import Location

#: Distanza di riferimento per il calcolo costi/durate.
_REFERENCE_DISTANCE: Final[float] = 1.0


class TransportError(Exception):
    """Errore di validazione trasporti."""


@dataclass(slots=True)
class TravelPlan:
    """Piano di viaggio multi-modale."""

    mode: TransportMode
    from_location_id: int
    to_location_id: int
    distance: float  # celle (approssimazione geometrica)
    duration_ticks: int
    cost: int  # Athel totali
    fuel_needed: float = 0.0
    route_id: int | None = None
    description: str = ""


@dataclass(slots=True)
class VehiclePurchaseResult:
    ok: bool
    reason: str
    vehicle_id: int | None = None
    cost_paid: int = 0


@dataclass(slots=True)
class TravelResult:
    ok: bool
    reason: str
    plan: TravelPlan | None = None
    cost_paid: int = 0
    fuel_consumed: float = 0.0


class TransportService:
    """Servizio stateless di trasporti."""

    # ------------------------------------------------------------------
    # Query veicoli
    # ------------------------------------------------------------------

    @staticmethod
    def daily_commute(
        session: Session,
        *,
        character: Character,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> TravelResult | None:
        """Sposta il character tra casa e lavoro (una volta al giorno).

        Con probabilità 50%: se è a casa va al lavoro, se è al lavoro va
        a casa. Sceglie il modo più veloce disponibile.
        """
        home_id = TransportService.home_location_id(session, character)
        work_id = TransportService.work_location_id(session, character)
        if home_id is None or work_id is None:
            return None
        if home_id == work_id:
            return None
        # Tira
        if rng.random() >= 0.5:
            return None

        target = work_id if character.location_id == home_id else home_id
        plan = TransportService.plan(
            session,
            character,
            from_location_id=character.location_id or home_id,
            to_location_id=target,
        )
        if plan is None:
            return None
        return TransportService.travel(
            session, character=character, plan=plan, current_dt=current_dt
        )

    @staticmethod
    def vehicle_of(
        session: Session, character_id: int, vehicle_type: VehicleType
    ) -> Vehicle | None:
        return session.scalars(
            select(Vehicle).where(
                Vehicle.owner_id == character_id,
                Vehicle.vehicle_type == vehicle_type.value,
            )
        ).first()

    @staticmethod
    def vehicles_of(session: Session, character_id: int) -> list[Vehicle]:
        return list(
            session.scalars(
                select(Vehicle)
                .where(Vehicle.owner_id == character_id)
                .order_by(Vehicle.vehicle_type)
            )
        )

    # ------------------------------------------------------------------
    # Acquisto veicolo
    # ------------------------------------------------------------------

    @staticmethod
    def buy_vehicle(
        session: Session,
        *,
        character: Character,
        vehicle_type: VehicleType,
        current_dt: AnthalysDateTime,
    ) -> VehiclePurchaseResult:
        if not character.is_alive:
            return VehiclePurchaseResult(False, "character_not_alive")
        existing = TransportService.vehicle_of(session, character.id, vehicle_type)
        if existing is not None:
            return VehiclePurchaseResult(False, f"already_has_{vehicle_type.value.lower()}")
        price = VEHICLE_PRICES.get(vehicle_type, 1000)
        if int(character.athel_balance) < price:
            return VehiclePurchaseResult(
                False,
                f"fondi insufficienti: {character.athel_balance} < {price}",
            )
        WealthService.add(
            session,
            character,
            -price,
            current_dt=current_dt,
            kind=JournalEntryKind.PURCHASE,
            description=f"Acquisto veicolo {vehicle_type.value}",
            reference_type="vehicle",
            metadata={"vehicle_type": vehicle_type.value, "price": price},
        )
        v = Vehicle(
            owner_id=character.id,
            vehicle_type=vehicle_type.value,
            fuel=100.0 if vehicle_type is VehicleType.CAR else 0.0,
            condition=1.0,
            location_id=character.location_id,
            is_parked=True,
            metadata_json={"bought_at": current_dt.to_total_seconds()},
        )
        session.add(v)
        session.flush()
        logger.info(
            "Vehicle bought: char={} type={} cost={}",
            character.id,
            vehicle_type.value,
            price,
        )
        return VehiclePurchaseResult(True, "ok", v.id, price)

    @staticmethod
    def refuel_car(session: Session, *, vehicle: Vehicle, amount_units: float = 30.0) -> float:
        """Rifornisce il veicolo. Ritorna il nuovo livello di carburante."""
        if vehicle.vehicle_type != VehicleType.CAR.value:
            return vehicle.fuel
        vehicle.fuel = min(100.0, vehicle.fuel + amount_units)
        session.flush()
        return vehicle.fuel

    # ------------------------------------------------------------------
    # Linee pubbliche
    # ------------------------------------------------------------------

    @staticmethod
    def all_routes(session: Session) -> list[TransportRoute]:
        return list(
            session.scalars(
                select(TransportRoute)
                .where(TransportRoute.is_active.is_(True))
                .order_by(TransportRoute.id)
            )
        )

    @staticmethod
    def stops_of(session: Session, route_id: int) -> list[RouteStop]:
        return list(
            session.scalars(
                select(RouteStop).where(RouteStop.route_id == route_id).order_by(RouteStop.sequence)
            )
        )

    @staticmethod
    def routes_serving_location(session: Session, location_id: int) -> list[TransportRoute]:
        stop_rows = list(
            session.scalars(select(RouteStop).where(RouteStop.location_id == location_id))
        )
        routes: list[TransportRoute] = []
        for stop in stop_rows:
            route = session.get(TransportRoute, stop.route_id)
            if route is not None and route.is_active:
                routes.append(route)
        return routes

    @staticmethod
    def create_route(
        session: Session,
        *,
        name: str,
        route_type: RouteType,
        stop_location_ids: list[int],
        base_fare: int | None = None,
        speed_cells_per_tick: float | None = None,
    ) -> TransportRoute:
        """Crea una linea con le sue fermate (ordine sequenziale)."""
        if len(stop_location_ids) < 2:
            raise TransportError("Una linea richiede almeno 2 fermate")
        fare = (
            base_fare
            if base_fare is not None
            else (BUS_FARE if route_type is RouteType.BUS else METRO_FARE)
        )
        speed = speed_cells_per_tick or (BUS_SPEED if route_type is RouteType.BUS else METRO_SPEED)
        route = TransportRoute(
            name=name,
            route_type=route_type.value,
            is_active=True,
            base_fare=fare,
            speed_cells_per_tick=speed,
            metadata_json={},
        )
        session.add(route)
        session.flush()
        for i, loc_id in enumerate(stop_location_ids):
            session.add(
                RouteStop(
                    route_id=route.id,
                    location_id=loc_id,
                    sequence=i,
                )
            )
        session.flush()
        logger.info(
            "Route created: {} ({}), {} stops",
            name,
            route_type.value,
            len(stop_location_ids),
        )
        return route

    # ------------------------------------------------------------------
    # Distanze
    # ------------------------------------------------------------------

    @staticmethod
    def _location_distance(session: Session, from_id: int, to_id: int) -> float:
        """Distanza geometrica (in celle) tra due Location."""
        if from_id == to_id:
            return 0.0
        a = session.get(Location, from_id)
        b = session.get(Location, to_id)
        if a is None or b is None:
            return 0.0
        ax, ay = a.center()
        bx, by = b.center()
        return math.hypot(ax - bx, ay - by)

    # ------------------------------------------------------------------
    # Plan
    # ------------------------------------------------------------------

    @staticmethod
    def plan(
        session: Session,
        character: Character,
        *,
        from_location_id: int,
        to_location_id: int,
    ) -> TravelPlan | None:
        """Ritorna il miglior piano di viaggio (costo minimo, tie-break velocità)."""
        plans = TransportService.plan_all(
            session,
            character,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
        )
        if not plans:
            return None
        # Ordina per (duration_ticks, cost)
        plans.sort(key=lambda p: (p.duration_ticks, p.cost))
        return plans[0]

    @staticmethod
    def plan_all(
        session: Session,
        character: Character,
        *,
        from_location_id: int,
        to_location_id: int,
    ) -> list[TravelPlan]:
        """Ritorna tutti i piani di viaggio disponibili, uno per modo.

        Distanza = costo A* su RoadTile se esiste un percorso, altrimenti
        distanza geometrica (fallback).
        """
        if from_location_id == to_location_id:
            return [
                TravelPlan(
                    mode=TransportMode.WALK,
                    from_location_id=from_location_id,
                    to_location_id=to_location_id,
                    distance=0.0,
                    duration_ticks=0,
                    cost=0,
                    description="già sul posto",
                )
            ]

        # Distanza: prova A* su strada, fallback geometrico
        from simai.city.transport.pathfinding import RoadGraph

        distance = 0.0
        used_road = False
        from_loc = session.get(Location, from_location_id)
        to_loc = session.get(Location, to_location_id)
        if from_loc is not None and to_loc is not None:
            graph = RoadGraph.from_session(session)
            if graph.node_count() > 0:
                ax, ay = from_loc.center()
                bx, by = to_loc.center()
                start_node = graph.nearest_node(int(ax), int(ay))
                goal_node = graph.nearest_node(int(bx), int(by))
                if start_node is not None and goal_node is not None:
                    path = graph.find_path(start_node, goal_node)
                    if path is not None:
                        distance = path.total_cost
                        used_road = True

        if not used_road or distance <= 0.0:
            distance = TransportService._location_distance(
                session, from_location_id, to_location_id
            )
            if distance <= 0.0:
                return []

        tag = "su strada" if used_road else "in linea d'aria"

        plans: list[TravelPlan] = []

        # 1. WALK (sempre)
        plans.append(
            TravelPlan(
                mode=TransportMode.WALK,
                from_location_id=from_location_id,
                to_location_id=to_location_id,
                distance=distance,
                duration_ticks=max(1, int(distance / WALK_SPEED)),
                cost=0,
                description=f"a piedi ({distance:.1f} {tag})",
            )
        )

        # 2. BIKE
        bike = TransportService.vehicle_of(session, character.id, VehicleType.BIKE)
        if bike is not None and bike.condition > 0.2:
            plans.append(
                TravelPlan(
                    mode=TransportMode.BIKE,
                    from_location_id=from_location_id,
                    to_location_id=to_location_id,
                    distance=distance,
                    duration_ticks=max(1, int(distance / BIKE_SPEED)),
                    cost=0,
                    description=f"in bici ({distance:.1f} {tag})",
                )
            )

        # 3. CAR
        car = TransportService.vehicle_of(session, character.id, VehicleType.CAR)
        if car is not None and car.condition > 0.2:
            fuel_needed = distance * CAR_FUEL_PER_CELL
            if car.fuel >= fuel_needed:
                cost = int(distance * CAR_FUEL_COST_PER_CELL)
                plans.append(
                    TravelPlan(
                        mode=TransportMode.CAR,
                        from_location_id=from_location_id,
                        to_location_id=to_location_id,
                        distance=distance,
                        duration_ticks=max(1, int(distance / CAR_SPEED)),
                        cost=cost,
                        fuel_needed=fuel_needed,
                        description=f"in auto ({distance:.1f} {tag})",
                    )
                )

        # 4. BUS
        bus_plan = TransportService._route_plan(
            session,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            route_type=RouteType.BUS,
            distance=distance,
        )
        if bus_plan is not None:
            plans.append(bus_plan)

        # 5. METRO
        metro_plan = TransportService._route_plan(
            session,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            route_type=RouteType.METRO,
            distance=distance,
        )
        if metro_plan is not None:
            plans.append(metro_plan)

        return plans

    @staticmethod
    def _route_plan(
        session: Session,
        *,
        from_location_id: int,
        to_location_id: int,
        route_type: RouteType,
        distance: float,
    ) -> TravelPlan | None:
        """Costruisce un TravelPlan per una linea pubblica (se esiste)."""
        routes_from = [
            r
            for r in TransportService.routes_serving_location(session, from_location_id)
            if r.route_type == route_type.value
        ]
        if not routes_from:
            return None
        for route in routes_from:
            stops = TransportService.stops_of(session, route.id)
            stop_ids = [s.location_id for s in stops]
            if to_location_id not in stop_ids:
                continue
            wait = BUS_WAIT_TICKS if route_type is RouteType.BUS else METRO_WAIT_TICKS
            travel_ticks = max(1, int(distance / route.speed_cells_per_tick))
            return TravelPlan(
                mode=(TransportMode.BUS if route_type is RouteType.BUS else TransportMode.METRO),
                from_location_id=from_location_id,
                to_location_id=to_location_id,
                distance=distance,
                duration_ticks=wait + travel_ticks,
                cost=int(route.base_fare),
                route_id=route.id,
                description=(
                    f"{route_type.value.lower()} '{route.name}' ({len(stop_ids)} fermate)"
                ),
            )
        return None

    # ------------------------------------------------------------------
    # Travel
    # ------------------------------------------------------------------

    @staticmethod
    def travel(
        session: Session,
        *,
        character: Character,
        plan: TravelPlan,
        current_dt: AnthalysDateTime,
    ) -> TravelResult:
        """Esegue il viaggio: muove il character, applica costi."""
        to_loc = session.get(Location, plan.to_location_id)
        if to_loc is None:
            return TravelResult(False, "destination_missing", plan)

        cost_paid = 0

        # 1. Costo biglietto (bus/metro)
        if plan.mode in (TransportMode.BUS, TransportMode.METRO):
            if int(character.athel_balance) < plan.cost:
                return TravelResult(
                    False,
                    f"fondi insufficienti per biglietto: {character.athel_balance} < {plan.cost}",
                    plan,
                )
            try:
                WealthService.add(
                    session,
                    character,
                    -plan.cost,
                    current_dt=current_dt,
                    kind=JournalEntryKind.PURCHASE,
                    description=f"Biglietto {plan.mode.value}",
                    reference_type="transit",
                    metadata={
                        "mode": plan.mode.value,
                        "route_id": plan.route_id,
                    },
                )
                cost_paid = plan.cost
            except EconomyError as exc:
                return TravelResult(False, f"wealth_error: {exc}", plan)

        # 2. Carburante (car)
        fuel_consumed = 0.0
        if plan.mode is TransportMode.CAR:
            car = TransportService.vehicle_of(session, character.id, VehicleType.CAR)
            if car is None or car.fuel < plan.fuel_needed:
                return TravelResult(False, "car_unavailable_or_no_fuel", plan)
            car.fuel = max(0.0, car.fuel - plan.fuel_needed)
            fuel_consumed = plan.fuel_needed
            # Sposta anche il veicolo
            car.location_id = plan.to_location_id

        # 3. Muove il character
        character.location_id = plan.to_location_id

        session.flush()
        logger.info(
            "Travel: char={} {} -> {} via {} ({} tick, {} Athel)",
            character.id,
            plan.from_location_id,
            plan.to_location_id,
            plan.mode.value,
            plan.duration_ticks,
            cost_paid,
        )
        return TravelResult(True, "ok", plan, cost_paid, fuel_consumed)

    # ------------------------------------------------------------------
    # Destination helpers
    # ------------------------------------------------------------------

    @staticmethod
    def home_location_id(session: Session, character: Character) -> int | None:
        """Location di casa (Lotto RESIDENTIAL posseduto dal character)."""
        from simai.economy.property import LotOwnershipService

        for o in LotOwnershipService.owned_by(session, character.id):
            lot = session.get(Lot, o.lot_id)
            if lot is not None and lot.usage == "RESIDENTIAL":
                return lot.location_id
        return None

    @staticmethod
    def work_location_id(session: Session, character: Character) -> int | None:
        """Location del posto di lavoro."""

        job = JobService.job_of(session, character.id)
        if job is None:
            return None
        return job.workplace_id

    @staticmethod
    def district_of_location(session: Session, location_id: int) -> District | None:
        """Trova il District che contiene la Location (via Lot)."""
        lot = session.scalars(select(Lot).where(Lot.location_id == location_id)).first()
        if lot is None:
            return None
        return session.get(District, lot.district_id)


__all__ = [
    "MAX_AI_TRIPS_PER_DAY",
    "MIN_WALK_DISTANCE_ALWAYS",
    "TransportError",
    "TransportService",
    "TravelPlan",
    "TravelResult",
    "VehiclePurchaseResult",
]
