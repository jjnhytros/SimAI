from typing import Dict, Optional, TYPE_CHECKING, cast
from .action_base import BaseAction
from core.enums import NeedType, ActionType, SkillType, FunActivityType, TraitType, Interest
from core.config import npc_config, time_config, actions_config

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class HaveFunAction(BaseAction):
    """Azione per divertirsi, con guadagno dinamico basato sulla personalità."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', 
                 activity_type: FunActivityType, **kwargs):
        config = actions_config.HAVEFUN_ACTIVITY_CONFIGS.get(activity_type, {})
        duration = int(config.get("duration_hours", 1.0) * time_config.TXH_SIMULATION)
        super().__init__(npc, simulation_context, duration_ticks=duration, **kwargs)
        
        self.activity_type = activity_type
        self.base_fun_gain_total = config.get("fun_gain", 0.0)
        self.base_skill_xp_gain_total = config.get("skill_xp_gain", 0.0)
        self.skill_to_practice = config.get("skill_to_practice")
        self.manages_need = NeedType.FUN

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        current_fun = self.npc.get_need_value(NeedType.FUN)
        if current_fun is not None and current_fun >= (npc_config.NEED_MAX_VALUE - 5.0):
            return False
        return True

    def execute_tick(self):
        super().execute_tick()
        if not self.is_started or self.is_finished: return

        base_gain_per_tick = self.base_fun_gain_total / self.duration_ticks if self.duration_ticks > 0 else 0
        personality_modifier = 1.0
        if self.activity_type == FunActivityType.DANCE and self.npc.has_trait(TraitType.PARTY_ANIMAL):
            personality_modifier = 2.0
        elif self.activity_type == FunActivityType.DANCE and self.npc.has_trait(TraitType.LONER):
            personality_modifier = 0.5
        
        interest_modifier = 1.0
        related_interest = actions_config.ACTIVITY_TO_INTEREST_MAP.get(cast(FunActivityType, self.activity_type))
        if related_interest and related_interest in self.npc.get_interests():
            interest_modifier = 1.5

        final_gain_this_tick = base_gain_per_tick * personality_modifier * interest_modifier
        self.npc.change_need_value(NeedType.FUN, final_gain_this_tick)

        base_xp_per_tick = self.base_skill_xp_gain_total / self.duration_ticks if self.duration_ticks > 0 else 0
        if self.skill_to_practice and base_xp_per_tick > 0:
            self.npc.skill_manager.add_experience(self.skill_to_practice, base_xp_per_tick)

    def on_finish(self):
        super().on_finish()
        if self.target_object:
            self.target_object.set_free()