from typing import Optional, TYPE_CHECKING, Dict
from core.enums import ActionType, NeedType
from .action_base import BaseAction
from core.config import time_config, actions_config, npc_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.world.game_object import GameObject

class UseBathroomAction(BaseAction):
    """Azione per usare il bagno. Il sollievo alla vescica è graduale."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', **kwargs):
        config = actions_config.SIMPLE_NEED_ACTION_CONFIGS.get(NeedType.BLADDER, {})
        duration = int(config.get("duration_hours", 0.25) * time_config.TXH_SIMULATION)

        super().__init__(npc, simulation_context, duration_ticks=duration, **kwargs)

        bladder_gain = config.get("bladder_gain", 100.0)
        self.gain_per_tick = bladder_gain / duration if duration > 0 else 0
        self.manages_need = NeedType.BLADDER
        
        self.effects_on_needs = {
            NeedType.HYGIENE: config.get("hygiene_gain", 15.0)
        }

    def is_valid(self) -> bool:
        if not super().is_valid() or not self.target_object or not self.target_object.is_available():
            return False
        return True

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and not self.is_finished:
            self.npc.change_need_value(NeedType.BLADDER, self.gain_per_tick)

    def on_finish(self):
        super().on_finish()
        if self.target_object:
            self.target_object.set_free()