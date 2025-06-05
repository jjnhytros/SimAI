# core/modules/skills/practical/cooking_skill.py
from typing import TYPE_CHECKING, List, Dict
from ..base_skill import BaseSkill
from core.enums.skill_types import SkillType
from core import settings # Per DEBUG_MODE, se necessario

if TYPE_CHECKING:
    from core.character import Character

class CookingSkill(BaseSkill):
    def __init__(self, character_owner: 'Character', initial_level: int = 0, initial_xp: float = 0.0):
        super().__init__(character_owner, SkillType.COOKING, initial_level, initial_xp)

    def on_level_up(self, new_level: int):
        super().on_level_up(new_level)
        if settings.DEBUG_MODE:
            if new_level == 2:
                print(f"    [{self.character_owner.name}] Ha sbloccato la ricetta 'Grilled Cheese' (Cucina Liv {new_level})")
            elif new_level == 5:
                print(f"    [{self.character_owner.name}] Ha sbloccato la ricetta 'Spaghetti' (Cucina Liv {new_level})")

    def get_level_benefits(self) -> Dict[int, List[str]]:
        return {
            1: ["Può preparare pasti semplici (es. Cereali)."],
            2: ["Sblocca 'Grilled Cheese'. Minore probabilità di bruciare cibo."],
            5: ["Sblocca 'Spaghetti'. Può preparare pasti di gruppo."],
            10: ["Master Chef: Sblocca piatti gourmet. Qualità eccellente."]
        }