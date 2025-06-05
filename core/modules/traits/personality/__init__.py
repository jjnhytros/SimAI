# core/modules/traits/personality/ambitious_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class AmbitiousTrait(BaseTrait):
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner, TraitType.AMBITIOUS)
        self.display_name = "Ambizioso"
        self.description = "Questo NPC ha grandi sogni e lavora sodo per raggiungere i suoi obiettivi."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Esempio: potrebbe dare un boost alle aspirazioni o alla performance lavorativa
        return None # Da definire

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # def get_action_choice_priority_modifier(self, action_type: 'ActionType') -> int:
    #     if action_type in [ActionType.ACTION_WORK, ActionType.ACTION_STUDY_SKILL]: # Nomi Enum da verificare
    #         return 10 # Più propenso a lavorare/studiare
    #     return 0