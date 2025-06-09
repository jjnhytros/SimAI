# core/AI/solution_discoverers/energy_discoverer.py
from typing import List, Optional, TYPE_CHECKING

from core.enums.action_types import ActionType
from core.enums.need_types import NeedType

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import ObjectType, LifeStage
from core.modules.actions import SleepAction, TravelToAction
from core.config import actions_config, time_config, npc_config

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class EnergySolutionDiscoverer(BaseSolutionDiscoverer):
    """Scopre tutte le possibili soluzioni per soddisfare il bisogno di ENERGY."""

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        
        # 1. Cerca un letto nella locazione attuale
        current_loc: Optional['Location'] = None
        if npc.current_location_id:
            current_loc = simulation_context.get_location_by_id(npc.current_location_id)

        if current_loc:
            for obj in current_loc.get_objects():
                if obj.object_type == ObjectType.BED and obj.is_available():
                    # Trovato! Crea un'azione per dormire qui.
                    sleep_action = self._create_sleep_action(npc, simulation_context, problem)
                    sleep_action.target_object = obj
                    if sleep_action.is_valid():
                        valid_actions.append(sleep_action)
                        return valid_actions

        # 2. Se non c'è un letto qui, cercalo in altre locazioni
        for loc_id, location in simulation_context.locations.items():
            if loc_id == npc.current_location_id: continue

            for obj in location.get_objects():
                if obj.object_type == ObjectType.BED:
                    # Trovato un letto in un'altra stanza! Pianifica un viaggio.
                    follow_up_action = self._create_sleep_action(npc, simulation_context, problem)
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

    def _create_sleep_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem') -> 'SleepAction':
        """Metodo helper per creare un'istanza di SleepAction con la configurazione corretta."""
        # Tutta la logica per determinare la durata del sonno ora è qui
        base_h = getattr(actions_config, 'SLEEP_ACTION_DEFAULT_HOURS', 7.0)
        adj_h = base_h
        if npc.life_stage:
            if npc.life_stage.is_child or npc.life_stage.is_teenager:
                adj_h = getattr(actions_config, 'SLEEP_HOURS_CHILD_TEEN', 9.0)
            elif npc.life_stage.is_elder:
                adj_h = getattr(actions_config, 'SLEEP_HOURS_ELDERLY', 8.0)
        
        return SleepAction(
            npc=npc,
            simulation_context=sim,
            duration_hours=adj_h,
            energy_gain_per_hour=getattr(actions_config, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', 15.0),
            validation_threshold=getattr(npc_config, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', 40.0),
            on_finish_energy_target=npc_config.NEED_MAX_VALUE,
            on_finish_needs_adjust={
                NeedType.HUNGER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_HUNGER', 70.0),
                NeedType.THIRST: getattr(actions_config, 'NEED_VALUE_ON_WAKE_THIRST', 75.0),
                NeedType.BLADDER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_BLADDER', 80.0)
            },
            triggering_problem=problem
        )