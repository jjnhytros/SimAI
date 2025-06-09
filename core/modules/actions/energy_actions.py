# core/modules/actions/energy_actions.py
from typing import Dict, Optional, TYPE_CHECKING, cast

from core.modules.memory.memory_definitions import Problem

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject
    from core.world.location import Location

from core.enums import NeedType, ActionType, ObjectType
from core.config import time_config, npc_config
from core import settings
from .action_base import BaseAction

class SleepAction(BaseAction):
    def __init__(self, npc: 'Character', 
                simulation_context: 'Simulation',
                duration_hours: float, energy_gain_per_hour: float,
                validation_threshold: float,
                on_finish_energy_target: float,
                on_finish_needs_adjust: Dict[NeedType, float],
                triggering_problem: Optional['Problem'] = None
                ):
        actual_duration_ticks = int(duration_hours * time_config.IXH)

        
        super().__init__(
            npc=npc,
            action_type_name="ACTION_SLEEP",
            action_type_enum=ActionType.ACTION_SLEEP,
            duration_ticks=actual_duration_ticks,
            p_simulation_context=simulation_context,
            is_interruptible=False, # Dormire è un'azione difficile da interrompere
            triggering_problem=triggering_problem
        )
        self.energy_gain_per_hour = energy_gain_per_hour
        self.validation_threshold = validation_threshold
        self.on_finish_energy_target = on_finish_energy_target
        self.on_finish_needs_adjust = on_finish_needs_adjust

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        current_energy = self.npc.get_need_value(NeedType.ENERGY)
        if current_energy is None or current_energy >= self.validation_threshold:
            return False

        if not self.target_object:
            if not self.sim_context or not self.npc.current_location_id: return False
            current_loc: Optional['Location'] = self.sim_context.get_location_by_id(self.npc.current_location_id)
            if not current_loc: return False

            bed = None
            for obj in current_loc.get_objects():
                if obj.object_type == ObjectType.BED and obj.is_available():
                    bed = obj
                    break
            
            if bed:
                self.target_object = bed
            else:
                return False
        
        return self.target_object.is_available()

    def on_start(self):
        super().on_start()
        if self.target_object:
            self.target_object.set_in_use(self.npc.npc_id)

    def _calculate_energy_gain(self) -> float:
        hours_slept = self.elapsed_ticks / time_config.IXH
        return hours_slept * cast(float, self.energy_gain_per_hour)

    def on_finish(self):
        if self.npc:
            current_energy = self.npc.get_need_value(NeedType.ENERGY) or 0
            self.npc.change_need_value(NeedType.ENERGY, self.on_finish_energy_target - current_energy)
            for need_type, target_value in self.on_finish_needs_adjust.items():
                current_value = self.npc.get_need_value(need_type) or 0
                self.npc.change_need_value(need_type, target_value - current_value)
        if self.target_object:
            self.target_object.set_free()
        super().on_finish()

    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        if self.npc:
            energy_gained = self._calculate_energy_gain()
            if energy_gained > 0:
                self.npc.change_need_value(NeedType.ENERGY, energy_gained)
        if self.target_object:
            self.target_object.set_free()