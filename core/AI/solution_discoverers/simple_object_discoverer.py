import importlib
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple, Union, Type

from .base_discoverer import BaseSolutionDiscoverer
from core.enums import ObjectType, NeedType
# Importiamo le azioni che ci servono
from core.modules.actions import BaseAction, TravelToAction
from core.modules.actions.movement_actions import MoveToAction
from core.utils.math_utils import calculate_distance
from core.config import time_config
from core import settings
from core.modules.actions import TravelToAction
from core.utils.global_pathfinder import find_best_route_plan

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class SimpleObjectDiscoverer(BaseSolutionDiscoverer):
    def __init__(self, action_config: Dict[str, Any]):
        self.action_config = action_config
        # Non salviamo più action_class qui, la caricheremo al momento
        self.required_object_types = action_config.get('required_objects', tuple())
        if not isinstance(self.required_object_types, tuple):
            self.required_object_types = (self.required_object_types,)

    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        # --- PASSO 1: Cerca un oggetto valido nella stanza attuale ---
        local_plan = self._discover_local_object(problem, npc, simulation_context)
        if local_plan:
            return local_plan # Se trova qualcosa, restituisce subito il piano

        # --- PASSO 2: Se non trova nulla, cerca in altre locazioni ---
        # Aggiungiamo un controllo sull'urgenza per evitare che un NPC viaggi per un bisogno minore
        if problem.urgency > 50: # Es: urgenza > 50 (su 144)
            remote_plan = self._discover_remote_object(problem, npc, simulation_context)
            if remote_plan:
                return remote_plan

        return [] # Se non trova assolutamente nulla, si arrende

    def _discover_local_object(self, problem: 'Problem', npc: 'Character', sim: 'Simulation') -> Optional[List['BaseAction']]:
        target_object = self._find_best_local_object(npc, sim)
        
        if target_object:
            try:
                path_str = self.action_config['action_class_path']
                module_path, class_name = path_str.rsplit('.', 1)
                action_module = importlib.import_module(module_path)
                action_class = getattr(action_module, class_name)

                action_params = {
                    'npc': npc,
                    'simulation_context': sim,
                    'triggering_problem': problem,
                    'target_object': target_object,
                }
                for key, value in self.action_config.items():
                    if key not in ['action_class_path', 'required_objects']:
                        if key == 'duration_hours':
                            action_params['duration_ticks'] = int(value * time_config.TXH_SIMULATION)
                        else:
                            action_params[key] = value
                
                final_action = action_class(**action_params)

            except (KeyError, ImportError, AttributeError, TypeError) as e:
                if settings.DEBUG_MODE:
                    print(f"[Discoverer ERROR] Impossibile creare l'istanza dell'azione locale: {e}")
                return None

            distance = calculate_distance((npc.logical_x, npc.logical_y), (target_object.logical_x, target_object.logical_y))
            if distance <= 1.5:
                if final_action.is_valid():
                    return [final_action]
            else:
                target_tile = self._find_adjacent_walkable_tile(target_object, npc, sim)
                if not target_tile: return None
                move_action = MoveToAction(npc, sim, target_tile[0], target_tile[1], follow_up_action=final_action)
                if move_action.is_valid():
                    return [move_action]
        return None

    def _find_best_local_object(self, npc: 'Character', simulation_context: 'Simulation') -> Optional['GameObject']:
        """Cerca tutti gli oggetti adatti nella locazione corrente e restituisce il più vicino."""
        if not npc.current_location_id: return None
        current_loc = simulation_context.get_location_by_id(npc.current_location_id)
        if not current_loc: return None

        valid_objects = [
            obj for obj in current_loc.get_objects()
            if obj.object_type in self.required_object_types and obj.is_available()
        ]
        
        if not valid_objects: return None

        if len(valid_objects) == 1:
            return valid_objects[0]
        else:
            npc_pos = (npc.logical_x, npc.logical_y)
            return min(valid_objects, key=lambda obj: calculate_distance(npc_pos, (obj.logical_x, obj.logical_y)))

    def _find_adjacent_walkable_tile(self, target_object: 'GameObject', npc: 'Character', simulation_context: 'Simulation') -> Optional[Tuple[int, int]]:
        """Trova una mattonella calpestabile adiacente all'oggetto target."""
        if not npc.current_location_id: return None
        location = simulation_context.get_location_by_id(npc.current_location_id)
        if not location or not location.walkable_grid: return None

        target_x, target_y = target_object.logical_x, target_object.logical_y
        adjacent_positions = [
            (target_x, target_y - 1), (target_x, target_y + 1),
            (target_x - 1, target_y), (target_x + 1, target_y),
        ]
        
        for x, y in adjacent_positions:
            if 0 <= y < location.logical_height and 0 <= x < location.logical_width:
                if location.walkable_grid[y][x]:
                    return (x, y) # Trovato un posto valido!
        
        return None

    def _discover_remote_object(self, problem: 'Problem', npc: 'Character', sim: 'Simulation') -> Optional[List['BaseAction']]:
        """Cerca un oggetto valido in tutto il mondo e pianifica un viaggio."""
        if not npc.current_location_id: return None

        for location in sim.locations.values():
            # Salta la locazione attuale
            if location.location_id == npc.current_location_id: continue

            for obj in location.get_objects():
                if obj.object_type in self.required_object_types and obj.is_available():
                    # Trovato un oggetto valido in un'altra locazione!
                    # Ora dobbiamo pianificare il viaggio
                    
                    # Calcola il percorso tra i distretti
                    # (Qui assumiamo che ogni location sia in un distretto omonimo per semplicità)
                    start_dist = npc.current_location_id # Es. "loc_dosinvelos_apt_01"
                    end_dist = location.location_id     # Es. "loc_muse_cafe_01"
                    
                    route_plan = find_best_route_plan(start_dist, end_dist)
                    
                    if route_plan:
                        # Abbiamo un piano di viaggio!
                        # Per ora, creiamo una singola TravelToAction. In futuro potremmo
                        # creare una coda di azioni basata su ogni "Route" del piano.
                        
                        # Calcola il tempo di viaggio totale
                        total_travel_time_min = sum(route.travel_time_minutes for route in route_plan)
                        travel_duration_ticks = int(total_travel_time_min * time_config.IXH * (1 / time_config.SECONDS_PER_SIMULATION_TICK))

                        # Crea l'azione finale da eseguire all'arrivo
                        final_action = self.action_class(npc=npc, simulation_context=sim, target_object=obj, **self.action_config)

                        # Crea l'azione di viaggio
                        travel_action = TravelToAction(
                            npc=npc,
                            simulation_context=sim,
                            destination_location_id=location.location_id,
                            duration_ticks=travel_duration_ticks,
                            follow_up_action=final_action
                        )
                        return [travel_action]
        return None