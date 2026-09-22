"""Enum del dominio terrain mode."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class TerrainType(StrEnum):
    """Tipo di suolo per una cella del lotto."""

    GRASS = "GRASS"
    DIRT = "DIRT"
    SAND = "SAND"
    STONE = "STONE"
    PAVEMENT = "PAVEMENT"
    FARMLAND = "FARMLAND"
    WATER = "WATER"
    ROCK = "ROCK"


#: Altezza massima (livelli 0..MAX_HEIGHT).
MAX_HEIGHT: Final[int] = 3

#: Terreni che non ammettono elevazione (devono stare a livello 0).
FLAT_ONLY: Final[frozenset[TerrainType]] = frozenset(
    {TerrainType.WATER, TerrainType.PAVEMENT, TerrainType.FARMLAND}
)

#: Terreni che bloccano la costruzione (muri/pavimenti non possono passarci).
BLOCKING_TERRAINS: Final[frozenset[TerrainType]] = frozenset({TerrainType.WATER, TerrainType.ROCK})

#: Cap di aggiornamenti di terrain al giorno (protezione).
MAX_TERRAIN_UPDATES_PER_DAY: Final[int] = 2000


__all__ = [
    "BLOCKING_TERRAINS",
    "FLAT_ONLY",
    "MAX_HEIGHT",
    "MAX_TERRAIN_UPDATES_PER_DAY",
    "TerrainType",
]
