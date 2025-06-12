# core/modules/traits/personality/good_trait.py
from typing import TYPE_CHECKING, Any, Dict, Optional
from ..base_trait import BaseTrait
from core.enums import TraitType, ActionType, SocialInteractionType

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.modules.actions.social_actions import SocializeAction

class GoodTrait(BaseTrait):
    """
    Rappresenta un NPC con una natura fondamentalmente buona, gentile e altruista.
    """
    
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.GOOD
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "È gentile, empatic* e cerca sempre di fare la cosa giusta."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        """Effetti da applicare quando il tratto viene aggiunto a un NPC."""
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        """Effetti da applicare quando il tratto viene rimosso."""
        # Per ora questo tratto non ha effetti alla rimozione
        return None

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

        # In futuro, potremmo aggiungere un bonus per azioni di volontariato o per aiutare gli altri
        
        return 1.0