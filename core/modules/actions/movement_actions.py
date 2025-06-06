# core/modules/actions/movement_actions.py
from typing import Optional, TYPE_CHECKING, List, Tuple
import math

# Import necessari
from core.enums import ActionType
from core import settings
from .action_base import BaseAction

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

# TODO: La durata del tick per muoversi di una "cella" dovrebbe essere in actions_config.py
# Esempio: TICKS_PER_TILE_MOVE = 5 
# Se un NPC deve muoversi di 10 celle, l'azione durerà 50 tick.
DEFAULT_TICKS_PER_TILE = 5 

class MoveToAction(BaseAction):
    """
    Azione per spostare un NPC a una specifica coordinata logica (x, y)
    all'interno della sua locazione corrente.
    """
    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation',
                destination: Tuple[int, int],
                follow_up_action: Optional[BaseAction] = None
                ):
        
        self.destination: Tuple[int, int] = destination
        self.follow_up_action: Optional[BaseAction] = follow_up_action
        self.path: List[Tuple[int, int]] = []
        
        distance = math.sqrt((self.destination[0] - npc.logical_x)**2 + (self.destination[1] - npc.logical_y)**2)
        duration_ticks = int(distance * getattr(settings, 'TICKS_PER_TILE_MOVE', 5))
        
        action_type_enum_val = ActionType.ACTION_MOVE_TO
        
        # --- CHIAMATA CORRETTA A super().__init__() ---
        super().__init__(
            npc=npc,
            action_type_name=action_type_enum_val.name, # <-- ARGOMENTO AGGIUNTO
            action_type_enum=action_type_enum_val,
            duration_ticks=max(1, duration_ticks),
            p_simulation_context=simulation_context,
            is_interruptible=True
        )
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. Destinazione: {self.destination}, Durata Stimata: {self.duration_ticks}t")

    def is_valid(self) -> bool:
        return True # Per ora, assumiamo che ogni movimento sia valido

    def on_start(self):
        super().on_start()
        # Pathfinding Semplificato (linea retta)
        start_x, start_y = self.npc.logical_x, self.npc.logical_y
        dest_x, dest_y = self.destination
        
        num_steps = self.duration_ticks
        if num_steps <= 0:
            self.path = [self.destination]
        else:
            for i in range(1, num_steps + 1):
                t = i / num_steps
                next_x = int(start_x * (1 - t) + dest_x * t)
                next_y = int(start_y * (1 - t) + dest_y * t)
                if not self.path or (next_x, next_y) != self.path[-1]:
                    self.path.append((next_x, next_y))
        
        if not self.path: self.path.append(self.destination)
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizio movimento verso {self.destination}. Percorso: {len(self.path)} passi.")

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and self.path:
            progress_ratio = self.get_progress_percentage()
            path_index = min(len(self.path) - 1, int(progress_ratio * len(self.path)))
            next_pos = self.path[path_index]
            self.npc.logical_x = next_pos[0]
            self.npc.logical_y = next_pos[1]

    def on_finish(self):
        self.npc.logical_x = self.destination[0]
        self.npc.logical_y = self.destination[1]
        
        if self.follow_up_action:
            if settings.DEBUG_MODE:
                print(f"    -> [{self.action_type_name} FINISH] Accodamento azione successiva: {self.follow_up_action.action_type_name}")
            self.npc.add_action_to_queue(self.follow_up_action)
            
        super().on_finish()
