# core/AI/solution_discoverers/fun_discoverer.py
from typing import List, Optional, TYPE_CHECKING, Tuple

from core.modules.actions.action_base import BaseAction

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import LocationType, NeedType, FunActivityType, ObjectType
from core.config import actions_config, time_config
from core.modules.actions import HaveFunAction, TravelToAction
from core.modules.actions.movement_actions import MoveToAction
from core.utils.math_utils import calculate_distance
from core import settings

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class FunSolutionDiscoverer(BaseSolutionDiscoverer):
    """
    Scopre attività di divertimento disponibili, sia locali (con o senza oggetti)
    che remote (richiedono di viaggiare).
    """

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        valid_actions: List['BaseAction'] = []
        if settings.DEBUG_MODE: print(f"\n--- [FunDiscoverer] Inizio ricerca per {npc.name} (FUN: {npc.get_need_value(NeedType.FUN):.1f}) ---")
        
        local_obj_actions = self._discover_local_object_activities(problem, npc, simulation_context)
        if local_obj_actions: valid_actions.extend(local_obj_actions)
        
        objectless_actions = self._discover_objectless_activities(problem, npc, simulation_context)
        if objectless_actions: valid_actions.extend(objectless_actions)
        
        if problem.urgency > 100:
            remote_actions = self._discover_remote_activities(problem, npc, simulation_context)
            if remote_actions: valid_actions.extend(remote_actions)
        
        if settings.DEBUG_MODE: print(f"--- [FunDiscoverer] Fine ricerca. Trovate {len(valid_actions)} opzioni valide. ---")
        return valid_actions

    def _discover_local_object_activities(self, problem: 'Problem', npc: 'Character', sim: 'Simulation') -> List['BaseAction']:
        actions = []
        if not npc.current_location_id: return actions
        current_loc = sim.get_location_by_id(npc.current_location_id)
        if not current_loc: return actions

        if settings.DEBUG_MODE: print("  [FunDiscoverer] Cerco attività locali CON OGGETTI...")
        available_objects = [obj for obj in current_loc.get_objects() if obj.is_available()]
        
        for activity_type, config in actions_config.HAVEFUN_ACTIVITY_CONFIGS.items():
            required_types = config.get("required_object_types")
            if not required_types: continue

            for obj in available_objects:
                if obj.object_type in required_types:
                    if settings.DEBUG_MODE: print(f"    -> Trovato oggetto '{obj.name}' per attività '{activity_type.name}'")
                    action_instance = HaveFunAction(npc, sim, activity_type, triggering_problem=problem)
                    plan = self._create_movement_plan_if_needed(npc, obj, action_instance, sim)
                    if plan:
                        if settings.DEBUG_MODE: print(f"      -> Creato piano valido: {plan.action_type_name}")
                        actions.append(plan)
                    else:
                        if settings.DEBUG_MODE: print(f"      -> Piano per '{obj.name}' non valido o non necessario.")
                    break
        return actions

    def _discover_objectless_activities(self, problem: 'Problem', npc: 'Character', sim: 'Simulation') -> List['BaseAction']:
        actions = []
        if settings.DEBUG_MODE: print("  [FunDiscoverer] Cerco attività locali SENZA OGGETTI...")
        for activity_type in actions_config.ACTIVITIES_WITHOUT_OBJECTS:
            if settings.DEBUG_MODE: print(f"    -> Considero '{activity_type.name}'")
            action = HaveFunAction(npc, sim, activity_type, triggering_problem=problem)
            if action.is_valid():
                if settings.DEBUG_MODE: print(f"      -> Creato azione valida: {action.action_type_name}")
                actions.append(action)
            else:
                if settings.DEBUG_MODE: print(f"      -> Azione '{activity_type.name}' non è valida.")
        return actions

    def _discover_remote_activities(self, problem, npc, sim) -> List['BaseAction']:
        # """Cerca luoghi divertenti in cui recarsi."""
        # actions = []
        # if settings.DEBUG_MODE: print("  [FunDiscoverer] Cerco attività REMOTE (viaggio)...")
        # for loc in sim.locations.values():
        #     if loc.location_type in {LocationType.CAFE, LocationType.JAZZ_CLUB, LocationType.MUSEUM}:
        #         # La logica qui può essere migliorata, per ora usiamo un'attività generica
        #         follow_up = HaveFunAction(npc, sim, FunActivityType.PEOPLE_WATCH, triggering_problem=problem)
        #         travel_action = TravelToAction(npc, sim, destination_location_id=loc.location_id, follow_up_action=follow_up)
        #         if travel_action.is_valid():
        #             actions.append(travel_action)
        # return actions
        return []
        
    # --- Metodi Helper per il Movimento (simili a SimpleObjectDiscoverer) ---

    def _create_movement_plan_if_needed(self, npc, target_object, follow_up_action, sim) -> Optional['BaseAction']:
        follow_up_action.target_object = target_object
        distance = calculate_distance((npc.logical_x, npc.logical_y), (target_object.logical_x, target_object.logical_y))
        
        if distance <= 1.5:
            if follow_up_action.is_valid():
                return follow_up_action
        else:
            target_tile = self._find_adjacent_walkable_tile(target_object, npc, sim)
            if target_tile:
                move_action = MoveToAction(npc, sim, target_tile[0], target_tile[1], follow_up_action=follow_up_action)
                if move_action.is_valid():
                    return move_action
        return None

    def _find_adjacent_walkable_tile(self, target_object, npc, sim) -> Optional[Tuple[int, int]]:
        if not npc.current_location_id: return None
        location = sim.get_location_by_id(npc.current_location_id)
        if not location or not location.walkable_grid: return None
        
        target_x, target_y = target_object.logical_x, target_object.logical_y
        for x, y in [(target_x, target_y - 1), (target_x, target_y + 1), (target_x - 1, target_y), (target_x + 1, target_y)]:
            if 0 <= y < location.logical_height and 0 <= x < location.logical_width and location.walkable_grid[y][x]:
                return (x, y)
        return None
