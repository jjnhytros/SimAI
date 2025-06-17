import random
from typing import Dict, Optional, TYPE_CHECKING, Set

from .action_base import BaseAction
from core.enums import NeedType, RelationshipType, ActionType
from core.config import actions_config, time_config, npc_config
from core import settings

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

class EngageIntimacyAction(BaseAction):
    """Azione per l'intimità. Guadagno di bisogno graduale, effetti su relazione alla fine."""

    def __init__(self, npc: 'Character', simulation_context: 'Simulation', 
                 target_npc: 'Character', **kwargs):
        config = actions_config.INTIMACY_ACTION_CONFIG.get(NeedType.INTIMACY, {})
        duration = int(config.get("duration_hours", 1.5) * time_config.TXH_SIMULATION)
        super().__init__(npc, simulation_context, duration_ticks=duration, **kwargs)
        
        self.target_npc = target_npc
        self.config = config
        self.manages_need = NeedType.INTIMACY

        initiator_gain = self.config.get("initiator_intimacy_gain", 0)
        self.initiator_gain_per_tick = initiator_gain / duration if duration > 0 else 0
        
        target_gain = self.config.get("target_intimacy_gain", 0)
        self.target_gain_per_tick = target_gain / duration if duration > 0 else 0
        
        self.relationship_score_gain = self.config.get("relationship_score_gain", 0)

    def is_valid(self) -> bool:
        if not super().is_valid() or not self.target_npc: return False

        # Controlla se il bisogno dell'iniziatore è abbastanza basso
        initiator_intimacy = self.npc.get_need_value(NeedType.INTIMACY)
        if initiator_intimacy is None or initiator_intimacy >= self.config.get("initiator_desire_threshold", 50):
            return False
            
        # Controlla il target
        if self.target_npc.is_busy: return False

        # Controlla la relazione
        relationship = self.npc.get_relationship_with(self.target_npc.npc_id)
        if not relationship: return False
        
        required_types = self.config.get("required_relationship_types", set())
        min_score = self.config.get("min_rel_score", 30)
        
        if relationship.type not in required_types or relationship.score < min_score:
            return False

        return True

    def on_start(self):
        super().on_start()
        if self.target_npc:
            self.target_npc.is_busy = True
            self.target_npc.current_action = self

    def execute_tick(self):
        super().execute_tick()
        if self.is_started and not self.is_finished and self.target_npc:
            self.npc.change_need_value(NeedType.INTIMACY, self.initiator_gain_per_tick)
            self.target_npc.change_need_value(NeedType.INTIMACY, self.target_gain_per_tick)

    def on_finish(self):
        super().on_finish()
        if self.npc and self.target_npc:
            current_relationship = self.npc.get_relationship_with(self.target_npc.npc_id)
            if current_relationship:
                self.npc.update_relationship(self.target_npc.npc_id, current_relationship.type, score_change=self.relationship_score_gain)
                self.target_npc.update_relationship(self.npc.npc_id, current_relationship.type, score_change=self.relationship_score_gain)
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