# core/modules/skills/children/motor_child_skill.py
from typing import TYPE_CHECKING, List, Dict
from ..base_skill import BaseSkill
from core.enums.skill_types import SkillType

if TYPE_CHECKING:
    from core.character import Character

class MotorChildSkill(BaseSkill):
    def __init__(self, character_owner: 'Character', initial_level: int = 0, initial_xp: float = 0.0):
        super().__init__(character_owner, SkillType.MOTOR_CHILD, initial_level, initial_xp)

    def get_level_benefits(self) -> Dict[int, List[str]]:
        return {
            1: ["Può impilare 2 blocchi."],
            3: ["Corre senza cadere spesso."],
            5: ["Può usare le altalene da solo."]
        }