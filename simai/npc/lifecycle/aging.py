"""AgingService — ricalcolo delle fasce di età."""

from __future__ import annotations

from dataclasses import dataclass

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.enums import LifeStagePediatric, LifeStagePsychosocial
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character


@dataclass(frozen=True, slots=True)
class AgeTransition:
    """Transizione di fascia di età rilevata per un Character."""

    character_id: int
    field: str  # "pediatric" | "psychosocial"
    old_stage: str
    new_stage: str


class AgingService:
    """Calcola le fasce di età e rileva transizioni. Stateless."""

    @staticmethod
    def compute_stages(
        character: Character, current_dt: AnthalysDateTime
    ) -> tuple[LifeStagePediatric, LifeStagePsychosocial]:
        """Calcola `(pediatric, psychosocial)` al tempo `current_dt`."""
        age_secs = LifeStageService.age_seconds_at(character.birth_total_seconds, current_dt)
        return (
            LifeStageService.get_pediatric_stage(age_secs),
            LifeStageService.get_psychosocial_stage(age_secs),
        )

    @staticmethod
    def apply_aging(character: Character, current_dt: AnthalysDateTime) -> list[AgeTransition]:
        """Aggiorna `life_stage_*` sul character. Ritorna le transizioni.

        Se il character non è ancora nato al `current_dt`, ritorna `[]`
        (nessuna transizione). Chiamante tipico: `LifecycleManager`.
        """
        age_secs = LifeStageService.age_seconds_at(character.birth_total_seconds, current_dt)
        if age_secs < 0:
            return []

        ped, psy = AgingService.compute_stages(character, current_dt)
        transitions: list[AgeTransition] = []

        if character.life_stage_pediatric != ped.value:
            transitions.append(
                AgeTransition(
                    character_id=character.id,
                    field="pediatric",
                    old_stage=character.life_stage_pediatric,
                    new_stage=ped.value,
                )
            )
            character.life_stage_pediatric = ped.value

        if character.life_stage_psychosocial != psy.value:
            transitions.append(
                AgeTransition(
                    character_id=character.id,
                    field="psychosocial",
                    old_stage=character.life_stage_psychosocial,
                    new_stage=psy.value,
                )
            )
            character.life_stage_psychosocial = psy.value

        return transitions


__all__ = ["AgeTransition", "AgingService"]
