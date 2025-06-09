# core/modules/actions/hunger_actions.py
from typing import Optional, TYPE_CHECKING, Dict

from core.enums import ActionType, NeedType, ObjectType
from .action_base import BaseAction
from core import settings
from core.config import npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location
    from core.modules.memory.memory_definitions import Problem

class EatAction(BaseAction):
    """Azione per l'NPC di mangiare, con gestione dell'oggetto sorgente di cibo."""

    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation', 
                duration_ticks: int, 
                hunger_gain: float,
                triggering_problem: Optional['Problem'] = None):
        
        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration_ticks,
            action_type_enum=ActionType.ACTION_EAT,
            triggering_problem=triggering_problem
        )
        self.hunger_gain = hunger_gain
        self.effects_on_needs = {NeedType.HUNGER: self.hunger_gain}

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        hunger_need = self.npc.needs.get(NeedType.HUNGER)
        if hunger_need and hunger_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        if not self.target_object:
            if not self.sim_context or not self.npc.current_location_id: return False
            current_loc: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc: return False

            food_source = None
            for obj in current_loc.get_objects():
                if obj.object_type == ObjectType.REFRIGERATOR and obj.is_available():
                    food_source = obj
                    break
            
            if food_source:
                self.target_object = food_source
            else:
                return False
        
        return self.target_object.is_available()

    def on_start(self):
        super().on_start()
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)

    def on_finish(self):
        if self.npc:
            for need_type, change_amount in self.effects_on_needs.items():
                self.npc.change_need_value(need_type, change_amount)
        if self.target_object:
            self.target_object.set_free()
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # Potremmo applicare effetti parziali qui se volessimo
        if self.target_object:
            self.target_object.set_free()