"""Package `simai.npc.economy` — denaro, inventario, proprietà, eredità."""

from simai.npc.economy.enums import InheritanceTier
from simai.npc.economy.inheritance import (
    MIN_SPOUSE_STRENGTH,
    SPOUSE_SHARE,
    InheritanceReport,
    InheritanceService,
)
from simai.npc.economy.models import CharacterOwnedLocation
from simai.npc.economy.service import (
    DEFAULT_LIVING_COST,
    EconomyError,
    InventoryService,
    PropertyService,
    ReconcileResult,
    WealthService,
)

__all__ = [
    "DEFAULT_LIVING_COST",
    "MIN_SPOUSE_STRENGTH",
    "SPOUSE_SHARE",
    "CharacterOwnedLocation",
    "EconomyError",
    "InheritanceReport",
    "InheritanceService",
    "InheritanceTier",
    "InventoryService",
    "PropertyService",
    "ReconcileResult",
    "WealthService",
]
