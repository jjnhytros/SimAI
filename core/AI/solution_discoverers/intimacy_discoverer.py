# core/AI/solution_discoverers/intimacy_discoverer.py
from typing import List, Optional, TYPE_CHECKING, Dict, Any

from core.enums.action_types import ActionType
from core.enums.need_types import NeedType

from .base_discoverer import BaseSolutionDiscoverer
from core.modules.actions import EngageIntimacyAction
from core.config import actions_config, time_config

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction

class IntimacySolutionDiscoverer(BaseSolutionDiscoverer):
    """
    Scopre se è possibile avviare un'azione di intimità, basandosi
    su un consenso precedentemente ottenuto.
    """

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []

        # 1. Controlla se esiste un consenso per l'intimità
        target_id = getattr(npc, 'pending_intimacy_target_accepted', None)
        if not target_id:
            # Nessun consenso, nessuna azione possibile
            return valid_actions
            
        target_character = simulation_context.get_npc_by_id(target_id)
        if not target_character:
             # Il target non è valido o non è più presente
            return valid_actions
        
        # 2. Crea un'istanza dell'azione di intimità
        action_instance = self._create_intimacy_action(
            npc, simulation_context, problem, target_character
        )

        # 3. Controlla se l'azione è valida (es. il target è nella stessa stanza e disponibile)
        if action_instance.is_valid():
            valid_actions.append(action_instance)
            
        return valid_actions

    def _create_intimacy_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem', target: 'Character') -> 'EngageIntimacyAction':
        """Metodo helper per creare un'istanza di EngageIntimacyAction."""

        return EngageIntimacyAction(
            npc=npc,
            simulation_context=sim,
            target_npc=target,
            duration_ticks=getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_DURATION_TICKS', int(time_config.IXH * 1)),
            initiator_intimacy_gain=getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_INITIATOR_GAIN', 60.0),
            target_intimacy_gain=getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_TARGET_GAIN', 60.0),
            relationship_score_gain=getattr(actions_config, 'INTIMACY_ACTION_DEFAULT_REL_GAIN', 15),
            triggering_problem=problem
        )