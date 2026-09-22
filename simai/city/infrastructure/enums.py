"""Enum e costanti del dominio infrastrutture."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class RoadType(StrEnum):
    """Tipo di strada."""

    PATH = "PATH"
    ALLEY = "ALLEY"
    STREET = "STREET"
    AVENUE = "AVENUE"


class RoadCondition(StrEnum):
    """Stato di manutenzione della strada."""

    NEW = "NEW"
    GOOD = "GOOD"
    WORN = "WORN"
    DAMAGED = "DAMAGED"
    RUINED = "RUINED"


class LightType(StrEnum):
    """Tipo di illuminazione pubblica."""

    STANDARD = "STANDARD"
    GAS = "GAS"
    ELECTRIC = "ELECTRIC"


#: Costo di posa per tipo di strada (Athel).
ROAD_COSTS: Final[dict[RoadType, int]] = {
    RoadType.PATH: 5,
    RoadType.ALLEY: 10,
    RoadType.STREET: 20,
    RoadType.AVENUE: 40,
}

#: Costo di installazione per tipo di lampione (Athel).
LIGHT_COSTS: Final[dict[LightType, int]] = {
    LightType.STANDARD: 30,
    LightType.GAS: 50,
    LightType.ELECTRIC: 80,
}

#: Raggio di copertura luminosa (in celle).
LIGHT_RADII: Final[dict[LightType, int]] = {
    LightType.STANDARD: 3,
    LightType.GAS: 4,
    LightType.ELECTRIC: 5,
}

#: Degrado giornaliero di condition.
ROAD_DAILY_DEGRADATION: Final[float] = 0.001
LIGHT_DAILY_DEGRADATION: Final[float] = 0.0005

#: Soglie di condition → fascia.
ROAD_CONDITION_THRESHOLDS: Final[dict[RoadCondition, float]] = {
    RoadCondition.NEW: 0.90,
    RoadCondition.GOOD: 0.70,
    RoadCondition.WORN: 0.40,
    RoadCondition.DAMAGED: 0.15,
    RoadCondition.RUINED: 0.0,
}

#: Sotto questa condizione, un lampione è spento.
LIGHT_OFF_CONDITION: Final[float] = 0.20

#: Cap operazioni infrastrutturali per giorno (protezione).
MAX_INFRASTRUCTURE_OPS_PER_DAY: Final[int] = 2000


def road_condition_from_value(value: float) -> RoadCondition:
    """Mappa un valore [0, 1] alla fascia di condition."""
    for condition in (
        RoadCondition.NEW,
        RoadCondition.GOOD,
        RoadCondition.WORN,
        RoadCondition.DAMAGED,
    ):
        if value >= ROAD_CONDITION_THRESHOLDS[condition]:
            return condition
    return RoadCondition.RUINED


__all__ = [
    "LIGHT_COSTS",
    "LIGHT_DAILY_DEGRADATION",
    "LIGHT_OFF_CONDITION",
    "LIGHT_RADII",
    "MAX_INFRASTRUCTURE_OPS_PER_DAY",
    "ROAD_CONDITION_THRESHOLDS",
    "ROAD_COSTS",
    "ROAD_DAILY_DEGRADATION",
    "LightType",
    "RoadCondition",
    "RoadType",
    "road_condition_from_value",
]
