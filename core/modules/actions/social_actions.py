# core/modules/actions/social_actions.py
"""
Definizione di SocializeAction, l'azione per le interazioni sociali tra NPC.
"""
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, RelationshipType, SocialInteractionType, ActionType, Gender
from core import settings
from .action_base import BaseAction

class SocializeAction(BaseAction):
    """
    Azione per eseguire una specifica interazione sociale tra due NPC.
    I parametri esatti dell'interazione vengono iniettati dall'AIDecisionMaker.
    """
    def __init__(self, 
                 npc: 'Character', 
                 simulation_context: 'Simulation',
                 target_npc: 'Character',
                 interaction_type: SocialInteractionType,
                 # --- Parametri di configurazione iniettati ---
                 duration_ticks: int,
                 initiator_social_gain: float,
                 target_social_gain: float,
                 relationship_score_change: int,
                 # Parametri opzionali per effetti più complessi
                 new_relationship_type_on_success: Optional[RelationshipType] = None,
                 effects_on_target: Optional[Dict[NeedType, float]] = None
                ):
        
        # Determina il nome specifico dell'azione e l'enum corrispondente
        action_name_str = f"ACTION_SOCIALIZE_{interaction_type.name}"
        action_type_enum = getattr(ActionType, action_name_str, ActionType.ACTION_SOCIALIZE)

        super().__init__(
            npc=npc,
            action_type_name=action_name_str,
            action_type_enum=action_type_enum,
            duration_ticks=duration_ticks,
            p_simulation_context=simulation_context, 
            is_interruptible=True
        )
        
        # Assegna gli attributi opzionali definiti in BaseAction
        self.target_npc = target_npc
        self.activity_type = interaction_type # Usa l'attributo generico per il tipo di interazione

        # Salva i parametri specifici dell'interazione come attributi
        self.initiator_social_gain = initiator_social_gain
        self.target_social_gain = target_social_gain
        self.relationship_score_change = relationship_score_change
        self.new_rel_type_on_success = new_relationship_type_on_success
        self.effects_on_target = effects_on_target or {}

        # L'effetto primario sull'iniziatore è sul bisogno SOCIAL
        self.effects_on_needs = {NeedType.SOCIAL: self.initiator_social_gain}

    def is_valid(self) -> bool:
        """Controlla se l'interazione sociale è valida nel contesto attuale."""
        if not super().is_valid(): return False
        
        target = self.target_npc
        
        if not target or self.npc == target:
            return False

        # Il target è disponibile per un'interazione?
        if target.is_busy and (not target.current_action or not target.current_action.is_interruptible):
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {target.name} è occupato (non interrompibile).")
            return False
        if target.current_action and target.current_action.action_type_enum == ActionType.ACTION_SLEEP:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {target.name} sta dormendo.")
            return False
        
        # La validazione specifica (es. punteggio relazione, attrazione)
        # è ora gestita da AIDecisionMaker prima di creare l'azione,
        # rendendo questo metodo più pulito.

        return True

    def on_start(self):
        super().on_start()
        # Occupa anche il target NPC per sincronizzare l'azione
        if self.target_npc:
            self.target_npc.is_busy = True
            self.target_npc.current_action = self 
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia '{self.interaction_type.display_name_it()}' con {self.target_npc.name}. Entrambi ora sono occupati.")

    def execute_tick(self):
        super().execute_tick()
        # Non è richiesta logica aggiuntiva qui, BaseAction gestisce il tempo.

    def _free_both_npcs(self):
        """Metodo helper per liberare entrambi gli NPC al termine o all'interruzione."""
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None
        # La liberazione di self.npc è gestita da Character.update_action, ma
        # resettare qui per sicurezza non fa male.
        if self.npc:
            self.npc.is_busy = False
            self.npc.current_action = None

    def on_finish(self):
        if not self.npc or not self.target_npc:
            super().on_finish()
            return
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Interazione terminata. Applico effetti...")
        
        # 1. Applica effetti sui bisogni
        self.npc.change_need_value(NeedType.SOCIAL, self.initiator_social_gain)
        self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain)
        if self.effects_on_target:
            for need_type, amount in self.effects_on_target.items():
                self.target_npc.change_need_value(need_type, amount)

        # 2. Aggiorna la relazione
        current_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
        rel_type_to_set = self.new_rel_type_on_success
        if rel_type_to_set is None and current_rel:
            rel_type_to_set = current_rel.type
        elif rel_type_to_set is None:
            rel_type_to_set = RelationshipType.ACQUAINTANCE
        
        self.npc.update_relationship(self.target_npc.npc_id, rel_type_to_set, score_change=self.relationship_score_change)
        self.target_npc.update_relationship(self.npc.npc_id, rel_type_to_set, score_change=self.relationship_score_change)

        # 3. Finalizza l'azione e libera gli NPC
        super().on_finish()
        self._free_both_npcs()
        if settings.DEBUG_MODE:
            print(f"    -> {self.npc.name} e {self.target_npc.name} sono di nuovo liberi.")


    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        
        if self.npc and self.target_npc and self.duration_ticks > 0:
            proportion_completed = self.elapsed_ticks / self.duration_ticks
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Interazione interrotta. Applico effetti parziali.")
            
            # Applica una frazione degli effetti, con una penalità
            penalty_factor = 0.5 
            self.npc.change_need_value(NeedType.SOCIAL, self.initiator_social_gain * proportion_completed * penalty_factor)
            self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain * proportion_completed * penalty_factor)
        
        # Libera entrambi gli NPC anche in caso di interruzione
        self._free_both_npcs()