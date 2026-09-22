"""CraftingAI — decisioni autonome di crafting per NPC."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Final

from loguru import logger
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.crafting.recipes import RECIPES, Recipe
from simai.npc.crafting.service import CraftingService
from simai.npc.models import Character
from simai.npc.skills.service import SkillService

#: Cap di craft al giorno per NPC.
MAX_CRAFTS_PER_DAY_PER_NPC: Final[int] = 3

#: Probabilità base di tentare un craft ad ogni tick (basso, è cumulativo).
BASE_TICK_PROBABILITY: Final[float] = 0.0015

#: Bonus di probabilità per livello della skill (lvl 20 → ×3).
SKILL_LEVEL_BONUS: Final[float] = 0.10

#: Location types ammessi per craftare (casa/negozio, no outdoor).
ALLOWED_LOCATION_TYPES: Final[frozenset[str]] = frozenset({"ROOM", "BUILDING", "SHOP"})


@dataclass(slots=True)
class CraftingTickReport:
    """Esito di un tentativo di craft AI."""

    attempted: bool
    success: bool
    recipe_code: str = ""
    reason: str = ""
    output_type: str = ""
    quality_label: str = ""
    skill_gained: bool = False


class CraftingAI:
    """Decisioni autonome di crafting."""

    @staticmethod
    def maybe_craft(
        session: Session,
        character: Character,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        crafts_today: int = 0,
    ) -> CraftingTickReport | None:
        """Tenta un craft se le condizioni sono soddisfatte.

        Ritorna:
          - `None` se non c'è nemmeno il tiro (skip veloce).
          - `CraftingTickReport` se ha tentato (con esito).

        Il chiamante gestisce il contatore `crafts_today` e lo resetta
        a cambio giorno.
        """
        if not character.is_alive:
            return None
        if crafts_today >= MAX_CRAFTS_PER_DAY_PER_NPC:
            return None
        if character.location_id is None:
            return None

        # Seleziona ricetta fattibile
        candidates = CraftingAI._find_feasible_recipes(session, character)
        if not candidates:
            return None

        # Tira la probabilità per la migliore candidata
        recipe, skill_level = candidates[0]
        prob = CraftingAI._craft_probability(skill_level)
        if rng.random() >= prob:
            return None

        # Esegui
        try:
            result = CraftingService.craft(
                session,
                character=character,
                recipe_code=recipe.code,
                current_dt=current_dt,
                rng=rng,
            )
        except Exception as exc:  # CraftingError o altro
            logger.warning("Crafting AI fallito per char={}: {}", character.id, exc)
            return CraftingTickReport(
                attempted=True,
                success=False,
                recipe_code=recipe.code,
                reason=f"exception: {exc}",
            )

        if not result.success:
            return CraftingTickReport(
                attempted=True,
                success=False,
                recipe_code=recipe.code,
                reason=result.reason,
            )

        logger.info(
            "Crafting AI: char={} recipe={} quality={} ({})",
            character.id,
            recipe.code,
            result.quality_value,
            result.quality_label.value,
        )
        return CraftingTickReport(
            attempted=True,
            success=True,
            recipe_code=recipe.code,
            reason="ok",
            output_type=result.output_type,
            quality_label=result.quality_label.value,
            skill_gained=result.skill_gained,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _craft_probability(skill_level: int) -> float:
        """Probabilità per tick, aumenta con la skill."""
        return BASE_TICK_PROBABILITY * (1.0 + SKILL_LEVEL_BONUS * skill_level)

    @staticmethod
    def _find_feasible_recipes(session: Session, character: Character) -> list[tuple[Recipe, int]]:
        """Ritorna `[(recipe, skill_level)]` fattibili, ordinate per
        rilevanza (skill più alta prima).
        """
        feasible: list[tuple[Recipe, int]] = []
        for recipe in RECIPES.values():
            skill = SkillService.get_skill(session, character.id, recipe.required_skill)
            lvl = skill.level if skill is not None else 0
            if lvl < recipe.min_skill_level:
                continue
            # Input presenti?
            missing = CraftingService.missing_inputs(session, character, recipe)
            if missing:
                continue
            feasible.append((recipe, lvl))

        # Ordina per: skill_level DESC, base_value DESC
        feasible.sort(key=lambda t: (-t[1], -t[0].base_value))
        return feasible


__all__ = [
    "ALLOWED_LOCATION_TYPES",
    "BASE_TICK_PROBABILITY",
    "MAX_CRAFTS_PER_DAY_PER_NPC",
    "SKILL_LEVEL_BONUS",
    "CraftingAI",
    "CraftingTickReport",
]
