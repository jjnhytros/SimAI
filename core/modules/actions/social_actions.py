import random
from typing import Dict, Optional, TYPE_CHECKING

from .action_base import BaseAction
from core.enums import NeedType, RelationshipType, SocialInteractionType, ActionType
from core.config import actions_config
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class SocializeAction(BaseAction):
    """Interazione sociale. Guadagno di bisogno graduale, effetti su relazione alla fine."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation',
                 target_npc: 'Character', interaction_type: SocialInteractionType, **kwargs):
        config = actions_config.SOCIALIZE_INTERACTION_CONFIGS.get(interaction_type, {})
        duration = config.get("duration_ticks", 20)
        super().__init__(npc, simulation_context, duration_ticks=duration, **kwargs)

        self.target_npc = target_npc
        self.interaction_type = interaction_type
        self.config = config
        self.manages_need = NeedType.SOCIAL
        
        initiator_gain = self.config.get("initiator_social_gain", 0)
        self.initiator_gain_per_tick = initiator_gain / duration if duration > 0 else 0
        
        target_gain = self.config.get("target_social_gain", 0)
        self.target_gain_per_tick = target_gain / duration if duration > 0 else 0

    def is_valid(self) -> bool:
        if not super().is_valid() or not self.target_npc or self.npc == self.target_npc:
            return False
        if self.target_npc.is_busy and (not self.target_npc.current_action or not self.target_npc.current_action.is_interruptible):
            return False
        return True

    def on_start(self):
        super().on_start()
        if self.target_npc:
            self.target_npc.is_busy = True
            self.target_npc.current_action = self
        if settings.DEBUG_MODE and self.npc and self.target_npc:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia '{self.interaction_type.name}' con {self.target_npc.name}.")

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and not self.is_finished and self.target_npc:
            self.npc.change_need_value(NeedType.SOCIAL, self.initiator_gain_per_tick)
            self.target_npc.change_need_value(NeedType.SOCIAL, self.target_gain_per_tick)

    def on_finish(self):
        super().on_finish()
        if not self.npc or not self.target_npc:
            self._free_both_npcs()
            return
            
        is_successful = random.random() < self.config.get("success_chance", 1.0)
        rel_change = self.config.get("rel_change_success", 0) if is_successful else self.config.get("rel_change_fail", 0)

        if is_successful:
            fun_gain = self.config.get("target_fun_gain", 0)
            if fun_gain > 0: self.target_npc.change_need_value(NeedType.FUN, fun_gain)

        current_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
        rel_type = current_rel.type if current_rel else RelationshipType.ACQUAINTANCE
        self.npc.update_relationship(self.target_npc.npc_id, rel_type, score_change=rel_change)
        self.target_npc.update_relationship(self.npc.npc_id, rel_type, score_change=rel_change)

        self._free_both_npcs()

    def _free_both_npcs(self):
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None
        if self.npc:
            self.npc.is_busy = False
            self.npc.current_action = None

    def on_interrupt_effects(self):
        """Quando interrotta, libera solo gli NPC. I guadagni parziali sono già stati applicati."""
        self._free_both_npcs()