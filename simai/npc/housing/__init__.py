"""Package `simai.npc.housing` — decisioni immobiliari AI."""

from simai.npc.housing.ai import HousingEvent, HousingReport, RealEstateAI
from simai.npc.housing.enums import (
    BROKE_THRESHOLD,
    BUY_HOME_PROBABILITY,
    BUY_SHOP_PROBABILITY,
    MAX_PURCHASES_PER_DAY,
    MIN_AGE_BUY,
    MIN_AGE_BUY_SHOP,
    MIN_RESERVE,
    MIN_SKILL_FOR_SHOP,
    SELL_PROBABILITY,
    SENIOR_AGE,
    HousingAction,
)

__all__ = [
    "BROKE_THRESHOLD",
    "BUY_HOME_PROBABILITY",
    "BUY_SHOP_PROBABILITY",
    "MAX_PURCHASES_PER_DAY",
    "MIN_AGE_BUY",
    "MIN_AGE_BUY_SHOP",
    "MIN_RESERVE",
    "MIN_SKILL_FOR_SHOP",
    "SELL_PROBABILITY",
    "SENIOR_AGE",
    "HousingAction",
    "HousingEvent",
    "HousingReport",
    "RealEstateAI",
]
