# core/modules/actions/intimacy_actions.py
from typing import TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, RelationshipType
from core import settings
from .action_base import BaseAction

_MODULE_DEFAULT_ENGAGE_INTIMACY_DURATION_TICKS: int = 60
_MODULE_DEFAULT_ENGAGE_INTIMACY_INITIATOR_GAIN: float = 50.0
_MODULE_DEFAULT_ENGAGE_INTIMACY_TARGET_GAIN: float = 50.0
_MODULE_DEFAULT_ENGAGE_INTIMACY_RELATIONSHIP_GAIN: int = 10.0

class EngageIntimacyAction(BaseAction):
    ACTION_TYPE_NAME = "ACTION_ENGAGE_INTIMACY"
    DISPLAY_NAME = "Intimità con partner" # Display name generico
    
    def __init__(self, 
                 npc: 'Character', 
                 target_npc: 'Character', 
                 simulation_context: Optional['Simulation'] = None,
                 duration_ticks: Optional[int] = None,
                 intimacy_gain: Optional[float] = None, # Potrebbe essere un unico valore o separato
                 relationship_gain: Optional[int] = None
                ):
        super().__init__(
            npc=npc,
            action_type_name=getattr(settings, f"{self.ACTION_TYPE_NAME}_NAME", self.ACTION_TYPE_NAME), # Permette override da settings se necessario
            duration_ticks=duration_ticks if duration_ticks is not None else \
                           getattr(settings, 'INTIMACY_ACTION_DURATION_TICKS', _MODULE_DEFAULT_ENGAGE_INTIMACY_DURATION_TICKS),
            simulation_context=simulation_context,
            is_interruptible=True,
            description=f"Sta avendo un momento di intimità con {target_npc.name}."
        )
        self.target_npc: 'Character' = target_npc
        
        self.initiator_intimacy_gain = intimacy_gain if intimacy_gain is not None else \
            getattr(settings, 'INTIMACY_ACTION_INITIATOR_GAIN', _MODULE_DEFAULT_ENGAGE_INTIMACY_INITIATOR_GAIN)
        self.target_intimacy_gain = getattr(settings, 'INTIMACY_ACTION_TARGET_GAIN', _MODULE_DEFAULT_ENGAGE_INTIMACY_TARGET_GAIN)
        self.relationship_score_gain = relationship_gain if relationship_gain is not None else \
            getattr(settings, 'INTIMACY_ACTION_REL_GAIN', _MODULE_DEFAULT_ENGAGE_INTIMACY_RELATIONSHIP_GAIN)

        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata con target {self.target_npc.name} (Durata: {self.duration_ticks}t)")

    # --- IMPLEMENTAZIONE CONCRETA DI IS_VALID ---
    def is_valid(self) -> bool:
        # if not super().is_valid(): return False # Se BaseAction avesse controlli futuri
        if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Inizio validazione per target {self.target_npc.name if self.target_npc else 'None'}.")

        if not self.npc or not self.target_npc or self.npc == self.target_npc:
            if settings.DEBUG_MODE and self.npc: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] NPC o Target non validi/uguali.")
            return False

        initiator_intimacy = self.npc.get_need_value(NeedType.INTIMACY)
        intimacy_desire_threshold = getattr(settings, 'INTIMACY_DESIRE_THRESHOLD', settings.NEED_LOW_THRESHOLD + 10)
        if initiator_intimacy is None or initiator_intimacy >= intimacy_desire_threshold:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno INTIMACY ({initiator_intimacy}) non abbastanza basso.")
            return False
            
        if self.target_npc.is_busy and (not self.target_npc.current_action or not self.target_npc.current_action.is_interruptible):
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} è occupato (non interrompibile).")
            return False
        if self.target_npc.current_action and self.target_npc.current_action.action_type_name == "ACTION_SLEEP":
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} sta dormendo.")
            return False
            
        relationship = self.npc.get_relationship_with(self.target_npc.npc_id)
        if not relationship:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessuna relazione con {self.target_npc.name}.")
            return False
        
        valid_relationship_types_for_intimacy = {
            RelationshipType.ROMANTIC_PARTNER, 
            RelationshipType.SPOUSE,
        }
        if relationship.type not in valid_relationship_types_for_intimacy:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Relazione con {self.target_npc.name} non idonea ({relationship.type.name}).")
            return False
        
        min_score = getattr(settings, "MIN_REL_SCORE_FOR_INTIMACY", 30)
        if relationship.score < min_score:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Punteggio relazione ({relationship.score}) < {min_score}.")
            return False

        target_intimacy_need = self.target_npc.get_need_value(NeedType.INTIMACY)
        if target_intimacy_need is not None and target_intimacy_need >= getattr(settings, "TARGET_INTIMACY_RECEPTIVENESS_THRESHOLD", settings.NEED_MAX_VALUE * 0.9): 
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} non sembra ricettivo (Intimacy: {target_intimacy_need:.1f}).")
            return False

        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Azione con {self.target_npc.name} considerata valida.")
        return True

    def on_start(self): # Già definito prima, assicurati sia corretto
        super().on_start() 
        self.target_npc.is_busy = True
        self.target_npc.current_action = self 
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia intimità con {self.target_npc.name}. Target reso occupato.")

    def execute_tick(self): # Già definito prima, assicurati sia corretto
        super().execute_tick()
        if self.is_started and settings.DEBUG_MODE:
            log_interval = max(1, self.duration_ticks // 4) 
            if self.ticks_elapsed > 0 and self.ticks_elapsed % log_interval == 0 and \
               self.ticks_elapsed < self.duration_ticks and not self.is_finished:
                print(f"    [{self.action_type_name} PROGRESS - {self.npc.name}] Momento di intimità con {self.target_npc.name}... ({self.get_progress_percentage():.0%})")

    def on_finish(self):
        # Chiamato quando l'azione di intimità è completata.
        # super().on_finish() verrà chiamato alla fine per gestire lo stato dell'azione dell'initiator.
        
        if self.npc and self.target_npc: 
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Intimità con {self.target_npc.name} terminata. Applico effetti.")
            
            # Applica guadagno al bisogno INTIMACY per entrambi
            self.npc.change_need_value(NeedType.INTIMACY, self.initiator_intimacy_gain)
            self.target_npc.change_need_value(NeedType.INTIMACY, self.target_intimacy_gain)
            
            # Migliora la relazione
            effective_rel_gain = self.relationship_score_gain
            current_relationship_npc_pov = self.npc.get_relationship_with(self.target_npc.npc_id)
            
            # Se sono già partner, l'intimità potrebbe rafforzare di più il legame
            if current_relationship_npc_pov and current_relationship_npc_pov.type in {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE}:
                bonus_rel_gain_partner = getattr(settings, "INTIMACY_REL_GAIN_BONUS_PARTNER", 5) # Esempio di bonus
                effective_rel_gain += bonus_rel_gain_partner
                if settings.DEBUG_MODE: print(f"        Bonus relazione partner applicato: +{bonus_rel_gain_partner}")

            # Determina il tipo di relazione da impostare/mantenere
            # Per EngageIntimacyAction, ci aspettiamo che la relazione sia già ROMANTIC_PARTNER o SPOUSE
            # e questa azione la rafforza. Non dovrebbe cambiare il tipo a meno di logiche future più complesse.
            rel_type_to_set = RelationshipType.ROMANTIC_PARTNER # Default se non c'è o per rafforzare
            if current_relationship_npc_pov and current_relationship_npc_pov.type in {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE}:
                rel_type_to_set = current_relationship_npc_pov.type
            
            self.npc.update_relationship(
                target_npc_id=self.target_npc.npc_id,
                new_type=rel_type_to_set,
                score_change=int(effective_rel_gain) # Assicurati che sia int
            )
            # Aggiorna anche la prospettiva del target
            self.target_npc.update_relationship(
                target_npc_id=self.npc.npc_id,
                new_type=rel_type_to_set, 
                score_change=int(effective_rel_gain)
            )
            
            if settings.DEBUG_MODE:
                print(f"        {self.npc.name} INTIMACY +{self.initiator_intimacy_gain:.1f}, {self.target_npc.name} INTIMACY +{self.target_intimacy_gain:.1f}")
                updated_rel = self.npc.get_relationship_with(self.target_npc.npc_id)
                if updated_rel:
                     print(f"        Relazione tra {self.npc.name} e {self.target_npc.name} aggiornata: Tipo={updated_rel.type.name}, Score={updated_rel.score}")
            
        # Chiamata al metodo on_finish della classe base per l'NPC iniziatore
        # Questo imposterà self.is_finished = True, self.is_started = False per questa azione
        # e Character.update_action si occuperà di resettare self.npc.current_action e self.npc.is_busy
        super().on_finish() 
        
        # Importante: Libera anche il target NPC, poiché era stato reso occupato da questa azione
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None # Assicura che il target non pensi di essere ancora in questa azione
            if settings.DEBUG_MODE:
                print(f"        Target {self.target_npc.name} liberato da EngageIntimacyAction.")

    def _on_cancel(self): 
        super()._on_cancel() 
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None
            if settings.DEBUG_MODE and self.npc: # self.npc potrebbe essere None se l'azione è cancellata molto presto
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name if self.npc else 'N/A'}] Azione con {self.target_npc.name} cancellata. Target liberato.")