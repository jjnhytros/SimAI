"""Package `simai.city.infrastructure` — strade e illuminazione pubblica."""

from simai.city.infrastructure.enums import (
    LIGHT_COSTS,
    LIGHT_DAILY_DEGRADATION,
    LIGHT_OFF_CONDITION,
    LIGHT_RADII,
    MAX_INFRASTRUCTURE_OPS_PER_DAY,
    ROAD_CONDITION_THRESHOLDS,
    ROAD_COSTS,
    ROAD_DAILY_DEGRADATION,
    LightType,
    RoadCondition,
    RoadType,
    road_condition_from_value,
)
from simai.city.infrastructure.models import RoadTile, StreetLight
from simai.city.infrastructure.service import (
    MAX_COORD,
    MAX_LIGHT_RADIUS,
    InfrastructureError,
    InfrastructureService,
    InfrastructureTickReport,
    PlaceResult,
)

__all__ = [
    "LIGHT_COSTS",
    "LIGHT_DAILY_DEGRADATION",
    "LIGHT_OFF_CONDITION",
    "LIGHT_RADII",
    "MAX_COORD",
    "MAX_INFRASTRUCTURE_OPS_PER_DAY",
    "MAX_LIGHT_RADIUS",
    "ROAD_CONDITION_THRESHOLDS",
    "ROAD_COSTS",
    "ROAD_DAILY_DEGRADATION",
    "InfrastructureError",
    "InfrastructureService",
    "InfrastructureTickReport",
    "LightType",
    "PlaceResult",
    "RoadCondition",
    "RoadTile",
    "RoadType",
    "StreetLight",
    "road_condition_from_value",
]
