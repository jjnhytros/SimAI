# core/modules/actions/social_actions.py
"""
Definizione di SocializeAction, l'azione per le interazioni sociali tra NPC.
"""
from typing import Dict, Optional, TYPE_CHECKING

# Import di base
from core.enums import NeedType, RelationshipType, SocialInteractionType, ActionType
from core import settings
from .action_base import BaseAction

# Import solo per il type-checking
if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.memory.memory_definitions import Problem

class SocializeAction(BaseAction):
    """
    Azione per eseguire una specifica interazione sociale tra due NPC.
    """
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation',
                 target_npc: 'Character',
                 interaction_type: SocialInteractionType,
                 duration_ticks: int,
                 initiator_social_gain: float,
                 target_social_gain: float,
                 relationship_score_change: int,
                 new_relationship_type_on_success: Optional[RelationshipType] = None,
                 effects_on_target: Optional[Dict[NeedType, float]] = None,
                 triggering_problem: Optional['Problem'] = None
                ):
        
        # Salviamo subito l'attributo specifico prima di chiamare super()
        self.interaction_type: SocialInteractionType = interaction_type
        
        super().__init__(
            npc=npc,
            p_simulation_context=simulation_context,
            duration_ticks=duration_ticks,
            action_type_name=f"ACTION_SOCIALIZE_{self.interaction_type.name}",
            action_type_enum=getattr(ActionType, f"ACTION_SOCIALIZE_{self.interaction_type.name}", ActionType.ACTION_SOCIALIZE),
            is_interruptible=True,
            triggering_problem=triggering_problem
        )
        
        # Assegna gli attributi opzionali definiti in BaseAction
        self.target_npc = target_npc
        self.activity_type = self.interaction_type

        # Salva i parametri specifici dell'interazione
        self.initiator_social_gain = initiator_social_gain
        self.target_social_gain = target_social_gain
        self.relationship_score_change = relationship_score_change
        self.new_rel_type_on_success = new_relationship_type_on_success
        self.effects_on_target = effects_on_target or {}

        self.effects_on_needs = {NeedType.SOCIAL: self.initiator_social_gain}

    def is_valid(self) -> bool:
        # L'assert qui garantisce che npc e target non siano None per il resto del metodo
        assert self.npc is not None, "L'iniziatore dell'azione non può essere None"
        assert self.target_npc is not None, "Il target dell'azione Socialize non può essere None"
        
        if not super().is_valid(): return False
        
        if self.npc == self.target_npc: return False

        if self.target_npc.is_busy and (not self.target_npc.current_action or not self.target_npc.current_action.is_interruptible):
            return False
        if self.target_npc.current_action and self.target_npc.current_action.action_type_enum == ActionType.ACTION_SLEEP:
            return False
            
        return True

    def on_start(self):
        super().on_start()
        
        # Garantiamo che il target esista prima di usarlo
        assert self.target_npc is not None
        
        self.target_npc.is_busy = True
        self.target_npc.current_action = self 
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia '{self.interaction_type.display_name_it()}' con {self.target_npc.name}.")

    def execute_tick(self):
        super().execute_tick()
        # Non è richiesta logica aggiuntiva qui, BaseAction gestisce il tempo.

    def _free_both_npcs(self):
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None
        if self.npc:
            self.npc.is_busy = False
            self.npc.current_action = None

    def on_finish(self):
        # Garantiamo che entrambi gli NPC esistano prima di procedere
        assert self.npc is not None and self.target_npc is not None
        
        # Tutti gli accessi seguenti sono ora sicuri per Pylance
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Interazione terminata. Applico effetti.")
        
        self.npc.change_need_value(NeedType.SOCIAL, self.initiator_social_gain)
        self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain)
        if self.effects_on_target:
            for need_type, amount in self.effects_on_target.items():
                self.target_npc.change_need_value(need_type, amount)

        current_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
        rel_type_to_set = self.new_rel_type_on_success or (current_rel.type if current_rel else RelationshipType.ACQUAINTANCE)
        
        self.npc.update_relationship(self.target_npc.npc_id, rel_type_to_set, score_change=self.relationship_score_change)
        self.target_npc.update_relationship(self.npc.npc_id, rel_type_to_set, score_change=self.relationship_score_change)

        super().on_finish()
        self._free_both_npcs()
        if settings.DEBUG_MODE:
            print(f"    -> {self.npc.name} e {self.target_npc.name} sono di nuovo liberi.")


    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        
        # Aggiungi un assert anche qui per sicurezza
        if self.npc and self.target_npc and self.duration_ticks > 0:
            proportion_completed = self.elapsed_ticks / self.duration_ticks
            penalty_factor = 0.5 
            self.npc.change_need_value(NeedType.SOCIAL, self.initiator_social_gain * proportion_completed * penalty_factor)
            self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain * proportion_completed * penalty_factor)
        
        self._free_both_npcs()
