"""Package `simai.world.terrain` — terrain mode (landscaping)."""

from simai.world.terrain.enums import (
    BLOCKING_TERRAINS,
    FLAT_ONLY,
    MAX_HEIGHT,
    MAX_TERRAIN_UPDATES_PER_DAY,
    TerrainType,
)
from simai.world.terrain.models import TerrainTile
from simai.world.terrain.palette import (
    TERRAIN_COLORS,
    TERRAIN_LABELS,
    lighten_hex,
)
from simai.world.terrain.service import (
    TERRAIN_BASE_COST,
    TERRAIN_ELEVATION_COST,
    TerrainApplyResult,
    TerrainService,
)

__all__ = [
    "BLOCKING_TERRAINS",
    "FLAT_ONLY",
    "MAX_HEIGHT",
    "MAX_TERRAIN_UPDATES_PER_DAY",
    "TERRAIN_BASE_COST",
    "TERRAIN_COLORS",
    "TERRAIN_ELEVATION_COST",
    "TERRAIN_LABELS",
    "TerrainApplyResult",
    "TerrainService",
    "TerrainTile",
    "TerrainType",
    "lighten_hex",
]
