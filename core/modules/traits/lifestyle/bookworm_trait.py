# core/modules/traits/lifestyle/bookworm_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.action_types import ActionType
from core.enums.fun_activity_types import FunActivityType
from core.enums.trait_types import TraitType
from core.modules.actions.fun_actions import HaveFunAction
from ..base_trait import BaseTrait # L'import di BaseTrait dalla directory genitore

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType # Se usato

class BookwormTrait(BaseTrait):
    trait_type = TraitType.BOOKWORM
    
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner)
        self.display_name = "Topo di Biblioteca"
        self.description = "Questo NPC ama leggere e impara più velocemente dai libri."

    def get_action_choice_priority_modifier(self, action, simulation_context):
        if isinstance(action, HaveFunAction) and action.activity_type == FunActivityType.READ_BOOK_FOR_FUN:
            return 2.0 # Forte preferenza per la lettura
        if action.action_type_enum == ActionType.ACTION_STUDY_AT_LIBRARY:
            return 1.5
        return 1.0

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Esempio: Aumenta il bisogno FUN quando legge, o la velocità di apprendimento da libri
        return {"initial_moodlet": "HAPPY_TO_READ"} # Esempio

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio di influenza sulle azioni o sui bisogni
    # def get_action_choice_priority_modifier(self, action_type: 'ActionType') -> int:
    #     if action_type == ActionType.ACTION_READ_BOOK: # Assumendo esista questa ActionType
    #         return 20 # Alta priorità per leggere
    #     return 0

    # def get_fun_satisfaction_modifier(self, action_type: 'ActionType', base_fun_gain: float) -> float:
    #     if action_type == ActionType.ACTION_READ_BOOK:
    #         return base_fun_gain * 1.5 # Ottiene più divertimento dalla lettura
    #     return base_fun_gain