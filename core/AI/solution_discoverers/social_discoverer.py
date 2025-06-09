# core/AI/solution_discoverers/social_discoverer.py
from typing import List, Optional, TYPE_CHECKING, Dict, Any, Tuple, Type, Union

from core.enums.object_types import ObjectType

from core.AI.solution_discoverers.base_discoverer import BaseSolutionDiscoverer
from core.enums import SocialInteractionType
from core.modules.actions import SocializeAction
from core.config import actions_config

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class SocialSolutionDiscoverer(BaseSolutionDiscoverer):
    """
    Scopre tutte le possibili interazioni sociali con gli NPC presenti nella stessa locazione.
    """
    def __init__(self, action_class: Type[BaseAction], required_object_types: Union[ObjectType, Tuple[ObjectType, ...]]):
        self.action_class = action_class
        self.required_object_types = required_object_types if isinstance(required_object_types, tuple) else (required_object_types,)

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        
        current_loc: Optional['Location'] = None
        if npc.current_location_id:
            current_loc = simulation_context.get_location_by_id(npc.current_location_id)
        if not current_loc or len(current_loc.npcs_present_ids) <= 1:
            # Non ci sono altre persone nella stanza, nessuna azione sociale possibile
            return valid_actions

        # Itera su ogni potenziale target nella locazione
        for target_id in current_loc.npcs_present_ids:
            if target_id == npc.npc_id:
                continue
            
            target_char = simulation_context.get_npc_by_id(target_id)
            if not target_char:
                continue

            # Per ogni target, itera su ogni possibile tipo di interazione sociale
            for interaction_type in SocialInteractionType:
                # Recupera la configurazione per questa specifica interazione
                interaction_config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type, {})
                
                # Controlla i prerequisiti (es. punteggio minimo di relazione)
                min_score_req = interaction_config.get("min_rel_score_req")
                if min_score_req is not None:
                    relationship = npc.get_relationship_with(target_char.npc_id)
                    if not relationship or relationship.score < min_score_req:
                        continue # Salta questa interazione, la relazione non è adatta

                # TODO: Aggiungere altri controlli di prerequisiti (es. tratti incompatibili)

                # Se i prerequisiti sono soddisfatti, crea un'istanza dell'azione
                action_instance = self._create_socialize_action(
                    npc, simulation_context, problem, 
                    target_char, interaction_type, interaction_config
                )

                # Aggiungila alla lista delle soluzioni valide solo se è eseguibile
                if action_instance.is_valid():
                    valid_actions.append(action_instance)
        
        return valid_actions

    def _create_socialize_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem', 
                                target: 'Character', interaction: 'SocialInteractionType', 
                                config: Dict[str, Any]) -> 'SocializeAction':
        """Metodo helper per creare un'istanza di SocializeAction con la configurazione corretta."""
        
        return SocializeAction(
            npc=npc,
            simulation_context=sim,
            target_npc=target,
            interaction_type=interaction,
            duration_ticks=config.get("duration_ticks", actions_config.SOCIALIZE_DEFAULT_DURATION_TICKS),
            initiator_social_gain=config.get("initiator_gain", actions_config.SOCIALIZE_DEFAULT_INITIATOR_GAIN),
            target_social_gain=config.get("target_gain", actions_config.SOCIALIZE_DEFAULT_TARGET_GAIN),
            relationship_score_change=config.get("rel_change", actions_config.SOCIALIZE_DEFAULT_REL_CHANGE),
            new_relationship_type_on_success=config.get("new_rel_type_on_success"),
            effects_on_target=config.get("effects_on_target"),
            triggering_problem=problem
        )