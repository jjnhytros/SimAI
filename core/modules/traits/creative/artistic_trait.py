# core/modules/traits/creative/artistic_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.fun_activity_types import FunActivityType
from core.enums.trait_types import TraitType
from core.modules.actions.fun_actions import HaveFunAction
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType

class ArtisticTrait(BaseTrait):
    trait_type = TraitType.ART_LOVER # Assicurati che esista nell'Enum
    
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner=character_owner, trait_type=TraitType.ARTISTIC)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Questo NPC ha un'anima artistica e trae grande gioia dalla creazione."

    def get_action_choice_priority_modifier(self, action, simulation_context):
        # Aumenta la priorità per azioni creative
        if isinstance(action, HaveFunAction) and action.activity_type in {FunActivityType.PAINT, FunActivityType.PLAY_GUITAR}:
            return 1.5
        return 1.0

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        return None # Da definire

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # def get_need_decay_modifier(self, need_type: 'NeedType') -> float:
    #     if need_type == NeedType.FUN and not self.character_owner.is_doing_artistic_activity():
    #         return 1.15 # Il divertimento scende più velocemente se non si dedica all'arte
    #     return 1.0