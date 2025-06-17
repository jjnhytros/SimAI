from typing import Optional, TYPE_CHECKING
from .action_base import BaseAction
from core.enums import ActionType, NeedType
from core.config import npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class EatAction(BaseAction):
    """Azione per mangiare. La fame viene soddisfatta gradualmente."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation',
                target_object: 'GameObject', duration_ticks: int, hunger_gain: float,
                **kwargs):
        
        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration_ticks,
            action_type_enum=ActionType.ACTION_EAT,
            **kwargs
        )
        
        self.target_object = target_object
        self.gain_per_tick = hunger_gain / duration_ticks if duration_ticks > 0 else 0
        self.manages_need = NeedType.HUNGER

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        hunger_need = self.npc.needs.get(NeedType.HUNGER)
        if hunger_need and hunger_need.get_value() >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False

        if not self.target_object or not self.target_object.is_available():
            return False
            
        return True

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and not self.is_finished:
            self.npc.change_need_value(NeedType.HUNGER, self.gain_per_tick)

    def on_finish(self):
        super().on_finish()
        if self.target_object:
            self.target_object.set_free()

    def on_interrupt_effects(self):
        if self.target_object:
            self.target_object.set_free()