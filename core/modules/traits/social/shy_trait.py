# core/modules/traits/social/shy_trait.py
from typing import TYPE_CHECKING

# Importa BaseTrait dal percorso corretto
from ..base_trait import BaseTrait
from core.enums import TraitType, ActionType
from core.config import npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions import BaseAction

class ShyTrait(BaseTrait):
    trait_type = TraitType.SHY
    display_name = "Timido"
    description = "Questo NPC si sente a disagio in grandi gruppi..."

    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner)
````````
    # Implementiamo il nuovo metodo che abbiamo aggiunto alla classe base
    def get_behavioral_action_modifier(self, action: 'BaseAction', simulation_context: 'Simulation') -> float:
        if action.action_type_enum == ActionType.ACTION_SOCIALIZE:
            # Ora usiamo self.character_owner, che sarà impostato correttamente
            owner_npc = self.character_owner 
            if not owner_npc or not owner_npc.current_location_id:
                return 1.0

            current_loc = simulation_context.get_location_by_id(owner_npc.current_location_id)
            if not current_loc or len(current_loc.npcs_present_ids) > npc_config.SHY_NPC_CROWD_THRESHOLD:
                return 0.1 # Penalizza pesantemente

        return 1.0
