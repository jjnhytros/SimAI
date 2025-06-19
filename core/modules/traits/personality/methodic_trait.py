from typing import TYPE_CHECKING
from ..base_trait import BaseTrait
from core.enums import TraitType

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions import BaseAction

class MethodicTrait(BaseTrait):
    """
    Questo NPC ama l'ordine e la routine.
    """
    
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = "Metodico"
        self.description = "Questo NPC ama l'ordine e la routine."

    def get_on_add_effects(self):
        # TODO: Aggiungere eventuali effetti quando il tratto viene aggiunto
        return None
        
    def get_on_remove_effects(self):
        # TODO: Aggiungere eventuali effetti quando il tratto viene rimosso
        return None
        
    def get_action_choice_priority_modifier(self, action: 'BaseAction', simulation_context: 'Simulation') -> float:
        # TODO: Aggiungere modificatori di punteggio per le azioni
        return 1.0

