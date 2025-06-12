# core/modules/traits/social/shy_trait.py
from typing import TYPE_CHECKING, Any, Dict, Optional

# Importa BaseTrait dal percorso corretto
from ..base_trait import BaseTrait
from core.enums import TraitType, ActionType
from core.config import npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions import BaseAction

class ShyTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.SHY
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Si sente a disagio in grandi gruppi e preferisce interagire con poche persone alla volta."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        """Effetti da applicare quando il tratto viene aggiunto a un NPC."""
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        """Effetti da applicare quando il tratto viene rimosso."""
        # Per ora questo tratto non ha effetti alla rimozione
        return None

    def get_behavioral_action_modifier(self, action, simulation_context):
        if action.action_type_enum == ActionType.ACTION_SOCIALIZE:
            owner_npc = self.character_owner
            if owner_npc and owner_npc.current_location_id:
                current_loc = simulation_context.get_location_by_id(owner_npc.current_location_id)
                if current_loc and len(current_loc.npcs_present_ids) > npc_config.SHY_NPC_CROWD_THRESHOLD:
                    return 0.1
        return 1.0
