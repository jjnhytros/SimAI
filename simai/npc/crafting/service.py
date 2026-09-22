"""CraftingService — esecuzione di ricette con skill-based quality."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.npc.crafting.enums import (
    QUALITY_JITTER_SIGMA,
    CraftingQuality,
    quality_from_value,
)
from simai.npc.crafting.recipes import Recipe, get_recipe
from simai.npc.skills.enums import MAX_SKILL_LEVEL
from simai.npc.skills.service import SkillService
from simai.world.models import GameObject

if TYPE_CHECKING:
    from simai.core.anthalys_datetime import AnthalysDateTime
    from simai.npc.models import Character


class CraftingError(Exception):
    """Errore di validazione crafting."""


@dataclass(frozen=True, slots=True)
class CraftResult:
    """Esito di un craft."""

    success: bool
    reason: str
    output_object_id: int | None = None
    output_type: str = ""
    output_quantity: int = 0
    quality_value: float = 0.0
    quality_label: CraftingQuality = CraftingQuality.POOR
    skill_gained: bool = False
    skill_level_after: int = 0


class CraftingService:
    """Servizio stateless di crafting."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def available_recipes(session: Session, character: Character) -> list[Recipe]:
        """Ritorna le ricette che il character può teoricamente tentare.

        Filtro: skill >= min_skill_level. Il check inventario è separato.
        """
        from simai.npc.crafting.recipes import all_recipes

        result: list[Recipe] = []
        for r in all_recipes():
            skill = SkillService.get_skill(session, character.id, r.required_skill)
            lvl = skill.level if skill is not None else 0
            if lvl >= r.min_skill_level:
                result.append(r)
        return result

    @staticmethod
    def inventory_count(session: Session, character: Character, item_type: str) -> int:
        """Quanti oggetti di tipo `item_type` possiede il character."""
        rows = session.scalars(
            select(GameObject).where(
                GameObject.owner_character_id == character.id,
                GameObject.type == item_type,
            )
        ).all()
        return len(list(rows))

    @staticmethod
    def missing_inputs(
        session: Session, character: Character, recipe: Recipe
    ) -> dict[str, tuple[int, int]]:
        """Ritorna `{input_type: (have, needed)}` per input mancanti."""
        missing: dict[str, tuple[int, int]] = {}
        for itype, needed in recipe.inputs.items():
            have = CraftingService.inventory_count(session, character, itype)
            if have < needed:
                missing[itype] = (have, needed)
        return missing

    # ------------------------------------------------------------------
    # Quality computation
    # ------------------------------------------------------------------

    @staticmethod
    def compute_quality(
        *,
        recipe: Recipe,
        skill_level: int,
        rng: random.Random,
    ) -> float:
        """Quality ∈ [0, 1]: skill-proportional + jitter gaussiano."""
        skill_factor = skill_level / MAX_SKILL_LEVEL
        base = recipe.base_quality + recipe.skill_quality_bonus * skill_factor
        jitter = rng.gauss(0.0, QUALITY_JITTER_SIGMA)
        return max(0.0, min(1.0, base + jitter))

    # ------------------------------------------------------------------
    # Craft
    # ------------------------------------------------------------------

    @staticmethod
    def craft(
        session: Session,
        *,
        character: Character,
        recipe_code: str,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> CraftResult:
        """Esegue un craft. Ritorna l'esito."""
        if not character.is_alive:
            return CraftResult(False, "character_not_alive")

        recipe = get_recipe(recipe_code)
        if recipe is None:
            return CraftResult(False, f"recipe_not_found:{recipe_code}")

        # 1. Skill check
        skill = SkillService.get_skill(session, character.id, recipe.required_skill)
        skill_level = skill.level if skill is not None else 0
        if skill_level < recipe.min_skill_level:
            return CraftResult(
                False,
                f"skill_too_low: {recipe.required_skill.value} "
                f"{skill_level} < {recipe.min_skill_level}",
            )

        # 2. Inventario check
        missing = CraftingService.missing_inputs(session, character, recipe)
        if missing:
            detail = ", ".join(f"{k} ({h}/{n})" for k, (h, n) in sorted(missing.items()))
            return CraftResult(False, f"missing_inputs: {detail}")

        # 3. Consuma input
        for itype, qty in recipe.inputs.items():
            CraftingService._consume(
                session,
                character_id=character.id,
                item_type=itype,
                quantity=qty,
            )

        # 4. Quality
        quality_value = CraftingService.compute_quality(
            recipe=recipe, skill_level=skill_level, rng=rng
        )
        quality_label = quality_from_value(quality_value)

        # 5. Crea output
        created: list[GameObject] = []
        for _ in range(recipe.output_quantity):
            obj = GameObject(
                name=recipe.output_name,
                type=recipe.output_type,
                location_id=character.location_id,
                owner_character_id=character.id,
                state="NEW",
                condition=1.0,
                container_capacity=None,
                container_contents_json=[],
                interactions_json=[],
                metadata_json={
                    "crafted": True,
                    "crafted_by": character.id,
                    "recipe_code": recipe.code,
                    "quality_value": round(quality_value, 4),
                    "quality_label": quality_label.value,
                    "base_value": recipe.base_value,
                    "crafted_at": current_dt.to_total_seconds(),
                },
            )
            session.add(obj)
            created.append(obj)
        session.flush()

        # 6. Skill XP
        skill_gained = False
        new_level = skill_level
        if skill is not None:
            xp = 15.0  # XP base per craft
            result = SkillService.add_progress(session, skill, xp_delta=xp, current_dt=current_dt)
            skill_gained = result is not None
            new_level = skill.level

        logger.info(
            "Craft: char={} recipe={} quality={:.2f} ({}) outputs={}",
            character.id,
            recipe.code,
            quality_value,
            quality_label.value,
            len(created),
        )

        return CraftResult(
            success=True,
            reason="ok",
            output_object_id=created[0].id if created else None,
            output_type=recipe.output_type,
            output_quantity=len(created),
            quality_value=quality_value,
            quality_label=quality_label,
            skill_gained=skill_gained,
            skill_level_after=new_level,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _consume(
        session: Session,
        *,
        character_id: int,
        item_type: str,
        quantity: int,
    ) -> None:
        """Consuma `quantity` oggetti di tipo `item_type`."""
        rows = list(
            session.scalars(
                select(GameObject)
                .where(
                    GameObject.owner_character_id == character_id,
                    GameObject.type == item_type,
                )
                .order_by(GameObject.id)
                .limit(quantity)
            )
        )
        if len(rows) < quantity:
            raise CraftingError(
                f"inventario insufficiente per {item_type}: {len(rows)} < {quantity}"
            )
        for r in rows:
            session.delete(r)
        session.flush()


__all__ = ["CraftResult", "CraftingError", "CraftingService"]
