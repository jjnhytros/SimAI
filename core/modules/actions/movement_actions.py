# core/modules/actions/movement_actions.py
from typing import Optional, List, Tuple, TYPE_CHECKING
from .action_base import BaseAction
from core.enums import ActionType
from core.utils.pathfinding import astar_pathfind
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class MoveToAction(BaseAction):
    """Azione che muove un NPC verso una coordinata specifica seguendo un percorso."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', 
                target_x: int, target_y: int, 
                follow_up_action: Optional['BaseAction'] = None,
                triggering_problem=None):
        
        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=-1,
            action_type_enum=ActionType.ACTION_MOVE_TO,
            triggering_problem=triggering_problem
        )
        self.target_pos = (target_x, target_y)
        self.path: Optional[List[Tuple[int, int]]] = None
        self.follow_up_action = follow_up_action
        
        if settings.DEBUG_MODE:
            # FIX: Usa self.target_pos invece di self.destination
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata. Destinazione: {self.target_pos}")

    def is_valid(self) -> bool:
        """Ora calcola il percorso qui per validare l'azione PRIMA che venga scelta."""
        if not super().is_valid(): return False
        
        if not self.npc.current_location_id: return False
        location = self.sim_context.get_location_by_id(self.npc.current_location_id)
        if not location or not location.walkable_grid: return False

        start_pos = (self.npc.logical_y, self.npc.logical_x)
        end_pos = (self.target_pos[1], self.target_pos[0])

        # Se siamo già a destinazione, l'azione non è "necessaria" ma è valida se c'è un follow-up.
        if start_pos == end_pos:
            self.is_finished = True
            return True

        self.path = astar_pathfind(location.walkable_grid, start_pos, end_pos)

        # L'azione è valida solo se un percorso esiste.
        return self.path is not None and len(self.path) > 1

    def on_start(self):
        """Ora si occupa solo di preparare il percorso già calcolato."""
        super().on_start()
        # Il percorso è già stato calcolato e validato in is_valid().
        # Dobbiamo solo rimuovere il primo passo (la posizione attuale).
        if self.path:
            self.path.pop(0)
            self.duration_ticks = len(self.path) # Aggiorna la durata per la UI
        else:
            # Se per qualche strano motivo il path non c'è, finisci subito.
            self.is_finished = True

    def execute_tick(self):
        super().execute_tick()
        if self.is_finished or self.is_interrupted: return

        if self.path:
            next_pos_y, next_pos_x = self.path.pop(0)
            self.npc.logical_x = next_pos_x
            self.npc.logical_y = next_pos_y
            if not self.path:
                self.is_finished = True
        else:
            self.is_finished = True

    def on_finish(self):
        if self.follow_up_action:
            self.npc.add_action_to_queue(self.follow_up_action)
        super().on_finish()
