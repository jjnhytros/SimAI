# core/modules/traits/personality/good_trait.py
from typing import TYPE_CHECKING
from ..base_trait import BaseTrait
from core.enums import TraitType, ActionType, SocialInteractionType

# --- AGGIUNGI QUESTO IMPORT ---
# Importiamo le classi Azione necessarie per i controlli di tipo
from core.modules.actions import BaseAction, SocializeAction
# --- FINE AGGIUNTA ---

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class GoodTrait(BaseTrait):
    """
    Rappresenta un NPC con una natura fondamentalmente buona, gentile e altruista.
    """
    
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = "Buono"
        self.description = "Questo NPC è gentile, empatico e cerca sempre di fare la cosa giusta."

    def get_action_choice_priority_modifier(self, action: 'BaseAction', simulation_context: 'Simulation') -> float:
        """
        Gli NPC buoni preferiscono le interazioni positive e detestano quelle negative.
        """
        if isinstance(action, SocializeAction):
            # Forte bonus per i complimenti
            if action.interaction_type == SocialInteractionType.COMPLIMENT:
                return 2.0
            
            # Forte penalità per i litigi
            if action.interaction_type == SocialInteractionType.ARGUE:
                return 0.2
        
        return 1.0

    def get_on_add_effects(self):
        return None
        
    def get_on_remove_effects(self):
        return None