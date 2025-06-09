# core/AI/solution_discoverers/simple_object_discoverer.py
from typing import List, Optional, TYPE_CHECKING, Tuple, Union, Type, Any, Dict

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import ObjectType, NeedType, LifeStage
from core.modules.actions import (
    BaseAction, TravelToAction, EatAction, DrinkAction, SleepAction, 
    UseBathroomAction, EngageIntimacyAction
)
from core.config import actions_config, time_config, npc_config
from core import settings

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.world.location import Location

class SimpleObjectDiscoverer(BaseSolutionDiscoverer):
    """
    Un discoverer generico per azioni che richiedono un tipo specifico di oggetto.
    """
    def __init__(self, action_class: Type[BaseAction], required_object_types: Union[ObjectType, Tuple[ObjectType, ...]]):
        self.action_class = action_class
        self.required_object_types = required_object_types if isinstance(required_object_types, tuple) else (required_object_types,)

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        need_to_address = problem.details.get('need')

        # FIX 1 & 2: Aggiungi un controllo di tipo all'inizio del metodo
        if not isinstance(need_to_address, NeedType):
            return valid_actions # Non possiamo procedere senza un bisogno valido

        # Ora 'need_to_address' è sicuramente un NeedType, quindi le chiamate seguenti sono sicure
        action_instance = self._create_action(npc, simulation_context, problem, need_to_address)
        
        if action_instance and action_instance.is_valid():
            valid_actions.append(action_instance)
            return valid_actions
        else:
            for loc_id, location in simulation_context.locations.items():
                if loc_id == npc.current_location_id: continue
                for obj in location.get_objects():
                    if obj.object_type in self.required_object_types and obj.is_available():
                        follow_up_action = self._create_action(npc, simulation_context, problem, need_to_address)
                        if follow_up_action:
                            travel_action = TravelToAction(
                                npc=npc, simulation_context=simulation_context,
                                destination_location_id=loc_id, follow_up_action=follow_up_action
                            )
                            if travel_action.is_valid():
                                valid_actions.append(travel_action)
                            return valid_actions
        
        return valid_actions

    def _create_action(self, npc: 'Character', sim: 'Simulation', problem: 'Problem', need: NeedType) -> Optional['BaseAction']:
        """Metodo helper per creare istanze di azioni semplici con le loro configurazioni."""
        action_configs: Dict[str, Any] = {}
        
        if self.action_class == EatAction:
            action_configs = {"duration_ticks": int(getattr(actions_config, 'EAT_ACTION_DEFAULT_DURATION_HOURS', 0.5) * time_config.IXH), "hunger_gain": getattr(actions_config, 'EAT_ACTION_DEFAULT_HUNGER_GAIN', 70.0)}
        elif self.action_class == DrinkAction:
            action_configs = {"drink_type_name": "WATER", "duration_ticks": int(getattr(actions_config, 'DRINK_DEFAULT_DURATION_HOURS', 0.2) * time_config.IXH), "thirst_gain": getattr(actions_config, 'DRINK_WATER_THIRST_GAIN', 60.0), "effects_on_other_needs": {NeedType.BLADDER: getattr(actions_config, 'DRINK_WATER_BLADDER_EFFECT', -10.0)}}
        elif self.action_class == UseBathroomAction:
            if need == NeedType.BLADDER:
                action_configs = {"for_need": need, "duration_ticks": getattr(actions_config, 'USEBATHROOM_TOILET_DURATION_TICKS', int(0.15 * time_config.IXH)), "bladder_relief": getattr(actions_config, 'USEBATHROOM_TOILET_BLADDER_RELIEF', 100.0), "hygiene_gain": getattr(actions_config, 'USEBATHROOM_TOILET_HYGIENE_GAIN', 15.0)}
            elif need == NeedType.HYGIENE:
                action_configs = {"for_need": need, "duration_ticks": getattr(actions_config, 'USEBATHROOM_SHOWER_DURATION_TICKS', int(0.4 * time_config.IXH)),"bladder_relief": 0.0, "hygiene_gain": getattr(actions_config, 'USEBATHROOM_SHOWER_HYGIENE_GAIN', 80.0)}
        elif self.action_class == SleepAction:
            # FIX 3: Dizionario completo per SleepAction
            base_h = getattr(actions_config, 'SLEEP_ACTION_DEFAULT_HOURS', 7.0)
            adj_h = base_h
            if npc.life_stage and (npc.life_stage.is_child or npc.life_stage.is_teenager):
                adj_h = getattr(actions_config, 'SLEEP_HOURS_CHILD_TEEN', 9.0)
            elif npc.life_stage and npc.life_stage.is_elder:
                adj_h = getattr(actions_config, 'SLEEP_HOURS_ELDERLY', 8.0)
            action_configs = {
                "duration_hours": adj_h,
                "energy_gain_per_hour": getattr(actions_config, 'SLEEP_ACTION_ENERGY_GAIN_PER_HOUR', 15.0),
                "validation_threshold": getattr(npc_config, 'ENERGY_THRESHOLD_TO_CONSIDER_SLEEP', (npc_config.NEED_LOW_THRESHOLD + 10)),
                "on_finish_energy_target": npc_config.NEED_MAX_VALUE,
                "on_finish_needs_adjust": {
                    NeedType.HUNGER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_HUNGER', 70.0),
                    NeedType.THIRST: getattr(actions_config, 'NEED_VALUE_ON_WAKE_THIRST', 75.0),
                    NeedType.BLADDER: getattr(actions_config, 'NEED_VALUE_ON_WAKE_BLADDER', 80.0)
                }
            }

        if not action_configs: return None
        
        params = {"npc": npc, "simulation_context": sim, "triggering_problem": problem, **action_configs}
        try:
            return self.action_class(**params)
        except TypeError as e:
            if settings.DEBUG_MODE: print(f"  [AI Discover] Errore parametri creando {self.action_class.__name__}: {e}")
            return None