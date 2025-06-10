# core/modules/traits/personality/childish_trait.py
from typing import TYPE_CHECKING
from ..base_trait import BaseTrait
from core.enums import TraitType, FunActivityType
from core.modules.actions import HaveFunAction

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction

class ChildishTrait(BaseTrait):
    trait_type = TraitType.CHILDISH
    
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner=character_owner, trait_type=self.trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Ha un animo fanciullesco e ama i giochi e gli scherzi, a volte in modo inappropriato per la sua età."

    def get_action_choice_priority_modifier(self, action: 'BaseAction', simulation_context: 'Simulation') -> float:
        # Questo tratto ADORA l'idea di saltare su una panchina
        if isinstance(action, HaveFunAction) and action.activity_type == FunActivityType.JUMP_ON_BENCH:
            return 6.0 # Bonus molto alto per un comportamento "folle"
        
        return 1.0