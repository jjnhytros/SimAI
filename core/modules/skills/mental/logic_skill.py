# core/modules/skills/mental/logic_skill.py
from typing import TYPE_CHECKING, List, Dict
from ..base_skill import BaseSkill
from core.enums.skill_types import SkillType

if TYPE_CHECKING:
    from core.character import Character

class LogicSkill(BaseSkill):
    def __init__(self, character_owner: 'Character', initial_level: int = 0, initial_xp: float = 0.0):
        super().__init__(character_owner, SkillType.LOGIC, initial_level, initial_xp)

    def get_level_benefits(self) -> Dict[int, List[str]]:
        return {
            1: ["Può giocare a scacchi a livello base."],
            3: ["Risolve puzzle più velocemente."],
            5: ["Sblocca interazione 'Dibattito Logico'."],
            7: ["Migliora le possibilità di successo in alcune carriere scientifiche."],
            10: ["Diventa un maestro di logica, può insegnare ad altri (Mentoring)."]
        }