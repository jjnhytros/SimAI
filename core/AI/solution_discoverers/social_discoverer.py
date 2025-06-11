# core/AI/solution_discoverers/social_discoverer.py
from typing import List, Optional, TYPE_CHECKING, Dict, Any, Set

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import SocialInteractionType, TraitType, Gender, RelationshipType, NeedType # Aggiungi gli import necessari
from core.modules.actions import SocializeAction
from core.config import actions_config
from core import settings # Aggiungi import settings se non presente

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class SocialSolutionDiscoverer(BaseSolutionDiscoverer):
    """
    Scopre interazioni sociali appropriate basandosi sulla personalità e relazione.
    """

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        
        # FIX 1: Controlla che l'ID della locazione esista prima di usarlo
        current_loc: Optional['Location'] = None
        if npc.current_location_id:
            current_loc = simulation_context.get_location_by_id(npc.current_location_id)

        if not current_loc or len(current_loc.npcs_present_ids) <= 1:
            return valid_actions

        for target_id in current_loc.npcs_present_ids:
            if target_id == npc.npc_id: continue
            
            target_char = simulation_context.get_npc_by_id(target_id)
            if not target_char: continue

            possible_interactions = self._get_possible_interactions(npc, target_char)
            
            for interaction_type in possible_interactions:
                interaction_config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type, {})
                
                # Spostiamo il controllo dei prerequisiti qui, è più pulito
                min_score_req = interaction_config.get("min_rel_score_req")
                if min_score_req is not None:
                    relationship = npc.get_relationship_with(target_char.npc_id)
                    if not relationship or relationship.score < min_score_req:
                        continue

                action_instance = self._create_socialize_action(
                    npc, simulation_context, problem, 
                    target_char, interaction_type, interaction_config
                )
                if action_instance.is_valid():
                    valid_actions.append(action_instance)
        
        return valid_actions

    def _get_possible_interactions(self, initiator: 'Character', target: 'Character') -> Set[SocialInteractionType]:
        """Seleziona un set di interazioni sociali appropriate."""
        possible: Set[SocialInteractionType] = {SocialInteractionType.TALK}
        
        if initiator.has_trait(TraitType.PLAYFUL):
            possible.add(SocialInteractionType.TELL_JOKE)
        
        # FIX 2: Usa solo il tratto GOOD, che sappiamo esistere
        if initiator.has_trait(TraitType.GOOD):
            possible.add(SocialInteractionType.COMPLIMENT)
            
        relationship = initiator.get_relationship_with(target.npc_id)
        if relationship and relationship.score > 30:
            possible.add(SocialInteractionType.DEEP_CONVERSATION)

        # La logica per flirt e litigi la lasciamo qui per ora
        # Potrebbe essere spostata in AIDecisionMaker se diventa più complessa
        if relationship and relationship.score > 10 and (target.gender in initiator.get_romantic_attraction()):
            possible.add(SocialInteractionType.FLIRT)
        if relationship and relationship.score < -20:
            possible.add(SocialInteractionType.ARGUE)

        return possible

    def _create_socialize_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem', 
                                target: 'Character', interaction: SocialInteractionType, 
                                config: Dict[str, Any]) -> 'SocializeAction':
        """Metodo helper per creare un'istanza di SocializeAction."""
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