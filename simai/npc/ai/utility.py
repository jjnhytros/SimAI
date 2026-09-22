"""AIDecisionMaker — utility pura su bisogni + tratti + skills + addictions + values."""

from __future__ import annotations

import random
from dataclasses import dataclass

from simai.npc.addictions.enums import CRAVING_BOOST_FACTOR, AddictionKind
from simai.npc.ai.actions import ACTION_CATALOG, Action
from simai.npc.needs.enums import NeedType
from simai.npc.needs.needs import Needs
from simai.npc.personality.enums import (
    VALUES_BOOST_MAX,
    VALUES_BOOST_MIN,
    VALUES_BOOST_SCALE,
    ValueAxis,
    action_values_alignment,
)
from simai.npc.skills.enums import SkillType
from simai.npc.traits.definitions import TRAIT_DEFS
from simai.npc.traits.enums import Trait


@dataclass(frozen=True, slots=True)
class ScoredAction:
    action: Action
    utility: float
    base_utility: float
    trait_modifier: float
    skill_boost: float = 1.0
    addiction_boost: float = 1.0
    values_boost: float = 1.0
    job_boost: float = 1.0


class AIDecisionMaker:
    """Sceglie l'azione con utility massima (tie-break casuale via RNG).

    Utility finale di un'azione:
        base         = Σ_needs (100 - needs[n]) * effects[n] / 100
        trait_mod    = Σ_traits utility_modifiers.get(action.type, 0) clamp [-0.8, +0.8]
        skill_boost  = 1 + (skill_level × action.utility_skill_boost)
        addiction_boost = 1 + (craving × CRAVING_BOOST_FACTOR)
        values_boost = 1 + VALUES_BOOST_SCALE × Σ_axis (values[axis] - 0.5) × alignment[axis]
        utility      = base × (1 + trait_mod) × skill_boost × addiction_boost × values_boost

    Filtri:
      - se `action.trains_skill` è impostato e `skill_level < min_skill_level`,
        l'azione è esclusa dal pool.
    """

    def __init__(self, min_utility: float = 0.5) -> None:
        if min_utility < 0:
            raise ValueError(f"min_utility deve essere >= 0, ricevuto {min_utility}")
        self._min_utility = min_utility

    @property
    def min_utility(self) -> float:
        return self._min_utility

    def score_all(
        self,
        needs: Needs,
        traits: list[Trait] | None = None,
        skill_levels: dict[SkillType, int] | None = None,
        addiction_cravings: dict[AddictionKind, float] | None = None,
        values: dict[ValueAxis, float] | None = None,
        job_skill: SkillType | None = None,
    ) -> list[ScoredAction]:
        """Calcola l'utility di tutte le azioni disponibili (filtrate)."""
        active_traits = traits if traits is not None else []
        levels = skill_levels if skill_levels is not None else {}
        cravings = addiction_cravings if addiction_cravings is not None else {}
        vals = values if values is not None else {}

        scored: list[ScoredAction] = []
        for action in ACTION_CATALOG:
            if not self._is_available(action, levels):
                continue
            base = self._base_utility(needs, action)
            # Job-aware training boost (Chunk 3.14)
            job_boost = 1.0
            if (
                job_skill is not None
                and action.trains_skill is not None
                and action.trains_skill == job_skill
            ):
                job_boost = 1.5
            modifier = self._trait_modifier(action, active_traits)
            boost = self._skill_boost(action, levels)
            addiction_boost = self._addiction_boost(action, cravings)
            values_boost = self._values_boost(action, vals)
            final = base * (1.0 + modifier) * boost * addiction_boost * values_boost * job_boost
            scored.append(
                ScoredAction(
                    action=action,
                    utility=final,
                    base_utility=base,
                    trait_modifier=modifier,
                    skill_boost=boost,
                    addiction_boost=addiction_boost,
                    values_boost=values_boost,
                )
            )
        scored.sort(key=lambda s: -s.utility)
        return scored

    def decide(
        self,
        needs: Needs,
        rng: random.Random,
        traits: list[Trait] | None = None,
        skill_levels: dict[SkillType, int] | None = None,
        addiction_cravings: dict[AddictionKind, float] | None = None,
        values: dict[ValueAxis, float] | None = None,
        job_skill: SkillType | None = None,
    ) -> Action | None:
        scored = self.score_all(needs, traits, skill_levels, addiction_cravings, values, job_skill)
        if not scored:
            return None
        best = scored[0]
        if best.utility < self._min_utility:
            return None
        threshold = best.utility - 0.5
        candidates = [s.action for s in scored if s.utility >= threshold]
        if len(candidates) == 1:
            return best.action
        return rng.choice(candidates)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _is_available(action: Action, levels: dict[SkillType, int]) -> bool:
        if action.trains_skill is None:
            return True
        current_level = levels.get(action.trains_skill, 0)
        return current_level >= action.min_skill_level

    @staticmethod
    def _base_utility(needs: Needs, action: Action) -> float:
        total = 0.0
        for need in NeedType:
            effect = action.effects.get(need, 0.0)
            if effect <= 0:
                continue
            deficit = 100.0 - needs.get(need)
            if deficit <= 0:
                continue
            total += deficit * effect / 100.0
        return total

    @staticmethod
    def _trait_modifier(action: Action, traits: list[Trait]) -> float:
        total = 0.0
        for trait in traits:
            tdef = TRAIT_DEFS.get(trait)
            if tdef is None:
                continue
            total += tdef.utility_modifiers.get(action.type, 0.0)
        return max(-0.8, min(0.8, total))

    @staticmethod
    def _skill_boost(action: Action, levels: dict[SkillType, int]) -> float:
        if action.trains_skill is None or action.utility_skill_boost <= 0.0:
            return 1.0
        level = levels.get(action.trains_skill, 0)
        return 1.0 + level * action.utility_skill_boost

    @staticmethod
    def _addiction_boost(action: Action, cravings: dict[AddictionKind, float]) -> float:
        if action.addiction_kind is None:
            return 1.0
        craving = cravings.get(action.addiction_kind, 0.0)
        if craving <= 0.0:
            return 1.0
        return 1.0 + craving * CRAVING_BOOST_FACTOR

    @staticmethod
    def _values_boost(action: Action, values: dict[ValueAxis, float]) -> float:
        """Boost basato su quanto l'azione è allineata ai valori del character."""
        if not values:
            return 1.0
        alignment = action_values_alignment(action.type)
        if not alignment:
            return 1.0
        total = 0.0
        for axis, align in alignment.items():
            current = values.get(axis, 0.5)
            total += (current - 0.5) * align
        boost = 1.0 + total * VALUES_BOOST_SCALE
        return max(VALUES_BOOST_MIN, min(VALUES_BOOST_MAX, boost))


__all__ = ["AIDecisionMaker", "ScoredAction"]
