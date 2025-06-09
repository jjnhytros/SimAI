# core/modules/traits/glutton_trait.py
"""
Definizione del tratto di personalità "Goloso" (Glutton).
Riferimento TODO: IV.3.b
"""
from typing import TYPE_CHECKING

from core.enums.trait_types import TraitType
from core.enums.need_types import NeedType # Per identificare il bisogno di Fame
from core.enums.action_types import ActionType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class GluttonTrait(BaseTrait):
    trait_type = TraitType.GLUTTON
    
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner)
        self.display_name = "Ghiottone"
        self.description = "Questo NPC ama il cibo e mangia più del necessario."

    def get_action_choice_priority_modifier(self, action, simulation_context):
        if action.action_type_enum == ActionType.ACTION_EAT:
            return 1.5 # Più propenso a scegliere di mangiare
        return 1.0

    def get_need_decay_modifier(self, need_type: NeedType, base_decay_rate: float) -> float: # Cambiato NeedTypeHint a NeedType
        if need_type == NeedType.HUNGER:
            return base_decay_rate * 1.5
        return base_decay_rate

    def get_need_urgency_modifier(self, need_type: NeedType, current_urgency_score: float) -> float: # Cambiato NeedTypeHint a NeedType
        if need_type == NeedType.HUNGER:
            return current_urgency_score * 1.3 
        return current_urgency_score

    def get_action_preference_modifier(self, action_type: ActionType, character: 'Character') -> float:
        """Aumenta la preferenza per l'azione di mangiare."""
        if action_type == ActionType.ACTION_EAT:
            return 1.5 # 50% più propenso a scegliere di mangiare (valore da bilanciare)
        return 1.0
