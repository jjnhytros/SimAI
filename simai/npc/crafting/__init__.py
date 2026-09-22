"""Package `simai.npc.crafting` — ricette e crafting skill-based."""

from simai.npc.crafting.ai import (
    BASE_TICK_PROBABILITY,
    MAX_CRAFTS_PER_DAY_PER_NPC,
    SKILL_LEVEL_BONUS,
    CraftingAI,
    CraftingTickReport,
)
from simai.npc.crafting.enums import (
    MAX_CRAFTS_PER_DAY,
    QUALITY_JITTER_SIGMA,
    QUALITY_PRICE_MULTIPLIER,
    CraftingQuality,
    quality_from_value,
)
from simai.npc.crafting.recipes import (
    RECIPES,
    RESOURCE_NAMES,
    RESOURCE_PRICES,
    Recipe,
    all_recipes,
    get_recipe,
)
from simai.npc.crafting.service import (
    CraftingError,
    CraftingService,
    CraftResult,
)

__all__ = [
    "BASE_TICK_PROBABILITY",
    "MAX_CRAFTS_PER_DAY",
    "MAX_CRAFTS_PER_DAY_PER_NPC",
    "QUALITY_JITTER_SIGMA",
    "QUALITY_PRICE_MULTIPLIER",
    "RECIPES",
    "RESOURCE_NAMES",
    "RESOURCE_PRICES",
    "SKILL_LEVEL_BONUS",
    "CraftResult",
    "CraftingAI",
    "CraftingError",
    "CraftingQuality",
    "CraftingService",
    "CraftingTickReport",
    "Recipe",
    "all_recipes",
    "get_recipe",
    "quality_from_value",
]
