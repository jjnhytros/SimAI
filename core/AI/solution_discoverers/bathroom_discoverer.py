# core/AI/solution_discoverers/bathroom_discoverer.py
from typing import List, Optional, TYPE_CHECKING, Tuple

from core.enums.action_types import ActionType

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import ObjectType, NeedType
from core.modules.actions import UseBathroomAction, TravelToAction
from core.config import actions_config, time_config

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class BathroomSolutionDiscoverer(BaseSolutionDiscoverer):
    """Scopre soluzioni per i bisogni BLADDER e HYGIENE."""

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        need_to_address = problem.details.get('need')

        if need_to_address not in {NeedType.BLADDER, NeedType.HYGIENE}:
            return valid_actions

        # 1. Determina quale tipo di oggetto cercare
        if need_to_address == NeedType.BLADDER:
            required_object_types: Tuple[ObjectType, ...] = (ObjectType.TOILET,)
        else: # HYGIENE
            required_object_types = (ObjectType.SHOWER, ObjectType.BATHTUB)

        # 2. Cerca l'oggetto nella locazione attuale
        current_loc: Optional['Location'] = None
        if npc.current_location_id:
            current_loc = simulation_context.get_location_by_id(npc.current_location_id)
        if current_loc:
            for obj in current_loc.get_objects():
                if obj.object_type in required_object_types and obj.is_available():
                    action = self._create_bathroom_action(npc, simulation_context, problem, need_to_address)
                    action.target_object = obj
                    if action.is_valid():
                        valid_actions.append(action)
                        return valid_actions

        # 3. Se non c'è un oggetto qui, cercalo in altre locazioni
        for loc_id, location in simulation_context.locations.items():
            if loc_id == npc.current_location_id: continue

            for obj in location.get_objects():
                if obj.object_type in required_object_types:
                    follow_up_action = self._create_bathroom_action(npc, simulation_context, problem, need_to_address)
                    travel_action = TravelToAction(
                        npc=npc,
                        simulation_context=simulation_context,
                        destination_location_id=loc_id,
                        follow_up_action=follow_up_action
                    )
                    if travel_action.is_valid():
                        valid_actions.append(travel_action)
                    return valid_actions
        
        return valid_actions

    def _create_bathroom_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem', need: 'NeedType') -> 'UseBathroomAction':
        """Metodo helper per creare un'istanza di UseBathroomAction con la configurazione corretta."""
        action_configs = {}
        if need == NeedType.BLADDER:
            action_configs = {
                "duration_ticks": getattr(actions_config, 'USEBATHROOM_TOILET_DURATION_TICKS', int(0.15 * time_config.IXH)),
                "bladder_relief": getattr(actions_config, 'USEBATHROOM_TOILET_BLADDER_RELIEF', 100.0),
                "hygiene_gain": getattr(actions_config, 'USEBATHROOM_TOILET_HYGIENE_GAIN', 15.0)
            }
        elif need == NeedType.HYGIENE:
            action_configs = {
                "duration_ticks": getattr(actions_config, 'USEBATHROOM_SHOWER_DURATION_TICKS', int(0.4 * time_config.IXH)),
                "bladder_relief": 0.0,
                "hygiene_gain": getattr(actions_config, 'USEBATHROOM_SHOWER_HYGIENE_GAIN', 80.0)
            }

        return UseBathroomAction(
            npc=npc,
            simulation_context=sim,
            for_need=need,
            triggering_problem=problem,
            **action_configs
        )