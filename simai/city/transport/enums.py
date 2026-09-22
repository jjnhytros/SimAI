"""Enum e costanti del dominio trasporti."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class TransportMode(StrEnum):
    """Modalità di trasporto disponibili."""

    WALK = "WALK"
    BIKE = "BIKE"
    CAR = "CAR"
    BUS = "BUS"
    METRO = "METRO"


class VehicleType(StrEnum):
    """Tipi di veicolo personale."""

    BIKE = "BIKE"
    CAR = "CAR"


class RouteType(StrEnum):
    """Tipo di linea pubblica."""

    BUS = "BUS"
    METRO = "METRO"


#: Velocità in celle/tick per modo (1 cella ≈ 1 km).
WALK_SPEED: Final[float] = 0.5
BIKE_SPEED: Final[float] = 1.9
CAR_SPEED: Final[float] = 5.0
BUS_SPEED: Final[float] = 3.0
METRO_SPEED: Final[float] = 7.5

#: Attesa base in tick (per bus/metro).
BUS_WAIT_TICKS: Final[int] = 5
METRO_WAIT_TICKS: Final[int] = 8

#: Tariffa base per corsa (Athel).
BUS_FARE: Final[int] = 2
METRO_FARE: Final[int] = 3

#: Costo carburante per cella (Athel / cella).
CAR_FUEL_COST_PER_CELL: Final[float] = 0.15

#: Consumo carburante per cella (unità fuel).
CAR_FUEL_PER_CELL: Final[float] = 1.5
BIKE_FUEL_PER_CELL: Final[float] = 0.0

#: Cap di viaggi AI al giorno (per NPC).
MAX_AI_TRIPS_PER_DAY: Final[int] = 4

#: Distanza minima (in celle) sotto cui si cammina sempre.
MIN_WALK_DISTANCE_ALWAYS: Final[float] = 3.0

#: Capacità passeggeri per veicolo.
VEHICLE_CAPACITY: Final[dict[VehicleType, int]] = {
    VehicleType.BIKE: 1,
    VehicleType.CAR: 4,
}

#: Prezzo acquisto veicolo (Athel).
VEHICLE_PRICES: Final[dict[VehicleType, int]] = {
    VehicleType.BIKE: 150,
    VehicleType.CAR: 2500,
}


__all__ = [
    "BIKE_FUEL_PER_CELL",
    "BIKE_SPEED",
    "BUS_FARE",
    "BUS_SPEED",
    "BUS_WAIT_TICKS",
    "CAR_FUEL_COST_PER_CELL",
    "CAR_FUEL_PER_CELL",
    "CAR_SPEED",
    "MAX_AI_TRIPS_PER_DAY",
    "METRO_FARE",
    "METRO_SPEED",
    "METRO_WAIT_TICKS",
    "MIN_WALK_DISTANCE_ALWAYS",
    "VEHICLE_CAPACITY",
    "VEHICLE_PRICES",
    "WALK_SPEED",
    "RouteType",
    "TransportMode",
    "VehicleType",
]
