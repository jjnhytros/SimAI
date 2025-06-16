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
        target_object = self._find_best_local_object(npc, simulation_context)
        
        if target_object:
            # --- NUOVA ISTRUZIONE DI DEBUG ---
            if settings.DEBUG_MODE:
                print(f"    [DISCOVERER CONFIG] self.action_config: {self.action_config}")
            # --- FINE DEBUG ---

            try:
                # 1. Carica dinamicamente la classe azione
                path_str = self.action_config['action_class_path']
                module_path, class_name = path_str.rsplit('.', 1)
                action_module = importlib.import_module(module_path)
                action_class = getattr(action_module, class_name)

                # 2. Prepara TUTTI i parametri richiesti dal costruttore dell'azione
                action_params = {
                    'npc': npc,
                    'simulation_context': simulation_context,
                    'triggering_problem': problem,
                    'target_object': target_object,
                }
                
                # Aggiunge i parametri dalla configurazione
                for key, value in self.action_config.items():
                    if key not in ['action_class_path', 'required_objects']:
                        if key == 'duration_hours':
                            action_params['duration_ticks'] = int(value * time_config.TXH_SIMULATION)
                        else:
                            action_params[key] = value
                
                # --- ISTRUZIONE DI DEBUG ---
                # Stampiamo il contenuto di action_params prima di chiamare il costruttore
                if settings.DEBUG_MODE:
                    print(f"    [DISCOVERER DEBUG] Parametri finali per {class_name}: {action_params}")
                
                # 3. Crea l'istanza dell'azione
                final_action = action_class(**action_params)

            except (KeyError, ImportError, AttributeError, TypeError) as e:
                if settings.DEBUG_MODE:
                    print(f"[Discoverer ERROR] Impossibile creare l'istanza dell'azione: {e}")
                return []
            
            # La logica di movimento rimane invariata
            distance = calculate_distance((npc.logical_x, npc.logical_y), (target_object.logical_x, target_object.logical_y))
            if distance <= 1.5:
                if final_action.is_valid():
                    return [final_action]
            else:
                target_tile = self._find_adjacent_walkable_tile(target_object, npc, simulation_context)
                if not target_tile: return []
                move_action = MoveToAction(
                    npc=npc, simulation_context=simulation_context,
                    target_x=target_tile[0], target_y=target_tile[1],
                    follow_up_action=final_action
                )
                if move_action.is_valid():
                    return [move_action]

        return []

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