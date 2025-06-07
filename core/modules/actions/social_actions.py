# core/modules/actions/social_actions.py
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, RelationshipType, SocialInteractionType, ActionType
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
        
        self.target_npc: 'Character' = target_npc
        self.interaction_type: SocialInteractionType = interaction_type

        # Salva i parametri specifici dell'interazione come attributi
        self.initiator_social_gain = initiator_social_gain
        self.target_social_gain = target_social_gain
        self.relationship_score_change = relationship_score_change
        self.new_rel_type_on_success = new_relationship_type_on_success
        self.effects_on_target = effects_on_target or {}

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
        
        self.effects_on_needs = {NeedType.SOCIAL: self.initiator_social_gain}

    def is_valid(self) -> bool:
        if not super().is_valid(): return False
        
        # Controlli di base sul target
        if not self.target_npc or self.npc == self.target_npc: return False
        
        # Controlla se il target è disponibile per un'interazione
        # Questa logica è fondamentale per evitare interazioni con NPC occupati o addormentati.
        if self.target_npc.is_busy and (not self.target_npc.current_action or not self.target_npc.current_action.is_interruptible):
            return False
        if self.target_npc.current_action and self.target_npc.current_action.action_type_enum == ActionType.ACTION_SLEEP:
            return False
            
        # Altri prerequisiti (come punteggio relazione minimo o attrazione per il FLIRT)
        # sono ora controllati da AIDecisionMaker prima di creare l'azione,
        # quindi questo metodo può essere più snello.

        return True

    def on_start(self):
        super().on_start()
        # CRUCIALE: Occupa anche il target NPC per sincronizzare l'azione
        self.target_npc.is_busy = True
        self.target_npc.current_action = self 
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia '{self.interaction_type.name}' con {self.target_npc.name}. Entrambi ora sono occupati.")

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
        self.npc.is_busy = False
        self.npc.current_action = None


    def on_finish(self):
        if not self.npc or not self.target_npc:
            super().on_finish()
            return
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Applico effetti completi.")
        
        # 1. Applica effetti sui bisogni (ora usa i valori d'istanza)
        self.npc.change_need_value(NeedType.SOCIAL, self.initiator_social_gain)
        self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain)
        if self.effects_on_target:
            for need_type, amount in self.effects_on_target.items():
                self.target_npc.change_need_value(need_type, amount)

        # 2. Aggiorna la relazione (ora usa i valori d'istanza)
        rel_type_to_set = self.new_rel_type_on_success
        if rel_type_to_set is None:
            current_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
            rel_type_to_set = current_rel.type if current_rel else RelationshipType.ACQUAINTANCE
        
        self.npc.update_relationship(self.target_npc.npc_id, rel_type_to_set, score_change=self.relationship_score_change)
        self.target_npc.update_relationship(self.npc.npc_id, rel_type_to_set, score_change=self.relationship_score_change)

        # 3. Libera entrambi gli NPC
        self._free_both_npcs()
        super().on_finish()
        if settings.DEBUG_MODE:
             print(f"    -> {self.npc.name} e {self.target_npc.name} sono di nuovo liberi.")


    def on_interrupt_effects(self):
        super().on_interrupt_effects()

        if self.npc and self.target_npc and self.duration_ticks > 0:
            proportion_completed = self.ticks_elapsed / self.duration_ticks
            
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Azione con {self.target_npc.name} interrotta. Applico effetti parziali.")

            # Applica effetti parziali sui bisogni
            self.npc.change_need_value(NeedType.SOCIAL, self.initiator_social_gain * proportion_completed * 0.5) # Penalità per interruzione
            self.target_npc.change_need_value(NeedType.SOCIAL, self.target_social_gain * proportion_completed * 0.5)
            # Potremmo non applicare il cambio di relazione se l'interazione è interrotta
        
        # Libera entrambi gli NPC anche in caso di interruzione
        self._free_both_npcs()