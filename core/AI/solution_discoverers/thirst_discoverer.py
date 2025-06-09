# core/AI/solution_discoverers/thirst_discoverer.py
from typing import List, Optional, TYPE_CHECKING

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import ObjectType, NeedType
from core.modules.actions import DrinkAction, TravelToAction
from core.config import actions_config, time_config

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction
    from core.world.location import Location

class ThirstSolutionDiscoverer(BaseSolutionDiscoverer):
    """Scopre tutte le possibili soluzioni per soddisfare il bisogno di THIRST."""

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        drink_source_types = {ObjectType.SINK, ObjectType.REFRIGERATOR, ObjectType.WATER_COOLER}

        # 1. Cerca una fonte d'acqua nella locazione attuale
        current_loc: Optional['Location'] = None
        if npc.current_location_id:
            current_loc = simulation_context.get_location_by_id(npc.current_location_id)
        if current_loc:
            for obj in current_loc.get_objects():
                if obj.object_type in drink_source_types and obj.is_available():
                    drink_action = self._create_drink_action(npc, simulation_context, problem)
                    drink_action.target_object = obj
                    if drink_action.is_valid():
                        valid_actions.append(drink_action)
                        return valid_actions

        # 2. Se non c'è una fonte qui, cercala in altre locazioni
        for loc_id, location in simulation_context.locations.items():
            if loc_id == npc.current_location_id: continue

            for obj in location.get_objects():
                if obj.object_type in drink_source_types:
                    follow_up_action = self._create_drink_action(npc, simulation_context, problem)
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

    def _create_drink_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem') -> 'DrinkAction':
        """Metodo helper per creare un'istanza di DrinkAction con la configurazione corretta."""
        # Per ora l'IA cerca solo acqua, ma questa logica può essere espansa
        drink_type_name = "WATER"
        
        default_duration = getattr(actions_config, 'DRINK_DEFAULT_DURATION_HOURS', 0.2)
        default_gain = getattr(actions_config, 'DRINK_DEFAULT_THIRST_GAIN', 40.0)
        
        config_duration = getattr(actions_config, f"DRINK_{drink_type_name.upper()}_DURATION_HOURS", default_duration)
        config_gain = getattr(actions_config, f"DRINK_{drink_type_name.upper()}_THIRST_GAIN", default_gain)
        
        effects = {NeedType.BLADDER: getattr(actions_config, 'DRINK_WATER_BLADDER_EFFECT', -10.0)}

        return DrinkAction(
            npc=npc,
            simulation_context=sim,
            drink_type_name=drink_type_name,
            duration_ticks=int(config_duration * time_config.IXH),
            thirst_gain=config_gain,
            effects_on_other_needs=effects,
            triggering_problem=problem
        )