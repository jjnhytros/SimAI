# core/modules/traits/personality/playful_trait.py
from typing import TYPE_CHECKING, Any, Dict, Optional
from ..base_trait import BaseTrait
from core.enums import TraitType, ActionType, SocialInteractionType
from core.modules.actions import BaseAction, SocializeAction

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class PlayfulTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.PLAYFUL
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Ama scherzare e divertirsi, e cerca sempre di alleggerire l'atmosfera."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        """Effetti da applicare quando il tratto viene aggiunto a un NPC."""
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        """Effetti da applicare quando il tratto viene rimosso."""
        # Per ora questo tratto non ha effetti alla rimozione
        return None

    def get_action_choice_priority_modifier(self, action: 'BaseAction', simulation_context: 'Simulation') -> float:
        # Incoraggia a raccontare barzellette
        if isinstance(action, SocializeAction) and action.interaction_type == SocialInteractionType.TELL_JOKE:
            return 1.8
        
        # Dà un piccolo bonus a tutte le azioni di divertimento
        if action.action_type_enum == ActionType.ACTION_HAVE_FUN:
            return 1.3
        
        return 1.0