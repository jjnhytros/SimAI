"""Enum e costanti del dominio crafting."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class CraftingQuality(StrEnum):
    """Fascia di qualità di un oggetto craftato."""

    POOR = "POOR"
    COMMON = "COMMON"
    GOOD = "GOOD"
    EXCELLENT = "EXCELLENT"


#: Soglie di skill per fasce di qualità (basate sul livello della skill richiesta).
SKILL_LEVEL_COMMON: Final[int] = 3
SKILL_LEVEL_GOOD: Final[int] = 8
SKILL_LEVEL_EXCELLENT: Final[int] = 14

#: Moltiplicatore del prezzo di rivendita per fascia qualità.
QUALITY_PRICE_MULTIPLIER: Final[dict[CraftingQuality, float]] = {
    CraftingQuality.POOR: 0.6,
    CraftingQuality.COMMON: 1.0,
    CraftingQuality.GOOD: 1.5,
    CraftingQuality.EXCELLENT: 2.5,
}

#: Cap di craft per giorno (protezione).
MAX_CRAFTS_PER_DAY: Final[int] = 200

#: Jitter applicato alla quality (deviazione standard).
QUALITY_JITTER_SIGMA: Final[float] = 0.05


def quality_from_value(value: float) -> CraftingQuality:
    """Mappa un valore [0, 1] a una fascia di qualità."""
    if value < 0.30:
        return CraftingQuality.POOR
    if value < 0.60:
        return CraftingQuality.COMMON
    if value < 0.85:
        return CraftingQuality.GOOD
    return CraftingQuality.EXCELLENT


__all__ = [
    "MAX_CRAFTS_PER_DAY",
    "QUALITY_JITTER_SIGMA",
    "QUALITY_PRICE_MULTIPLIER",
    "SKILL_LEVEL_COMMON",
    "SKILL_LEVEL_EXCELLENT",
    "SKILL_LEVEL_GOOD",
    "CraftingQuality",
    "quality_from_value",
]
