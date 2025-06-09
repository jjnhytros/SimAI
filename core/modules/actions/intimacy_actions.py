# core/modules/actions/intimacy_actions.py
from typing import TYPE_CHECKING, Optional, Dict

from core.modules.memory.memory_definitions import Problem

if TYPE_CHECKING:
    from core.character import Character
    from core.simulation import Simulation

from core.enums import NeedType, RelationshipType, ActionType 
from core import settings
# from core.config import time_config # Se necessario per calcolare durate di default in AIDecisionMaker
from .action_base import BaseAction

# Rimuoviamo i _MODULE_DEFAULT qui perché i valori verranno iniettati
# _MODULE_DEFAULT_ENGAGE_INTIMACY_DURATION_TICKS: int = 60
# _MODULE_DEFAULT_ENGAGE_INTIMACY_INITIATOR_GAIN: float = 50.0
# ... e così via

class EngageIntimacyAction(BaseAction):
    def __init__(self, 
                npc: 'Character', 
                simulation_context: 'Simulation',
                target_npc: 'Character', # Parametro target esplicito
                # --- Parametri di configurazione ora iniettati ---
                duration_ticks: int,
                initiator_intimacy_gain: float,
                target_intimacy_gain: float,
                relationship_score_gain: int,
                triggering_problem: Optional['Problem'] = None,

                # Potresti aggiungere altri parametri se necessario, es:
                # required_relationship_types: Set[RelationshipType] = {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE}
                ):
        
        action_type_enum_val = ActionType.ACTION_ENGAGE_INTIMACY # Assicurati che esista in ActionType

        super().__init__(
            npc=npc,
            action_type_name=action_type_enum_val.name, # Derivato dall'enum
            action_type_enum=action_type_enum_val,
            duration_ticks=duration_ticks, # Usa il parametro iniettato
            p_simulation_context=simulation_context,
            is_interruptible=True,
            triggering_problem=triggering_problem,
        )
        self.target_npc = target_npc
        
        # Salva i parametri specifici dell'azione
        self.initiator_intimacy_gain: float = initiator_intimacy_gain
        self.target_intimacy_gain: float = target_intimacy_gain
        self.relationship_score_gain: int = relationship_score_gain
        # self.required_relationship_types = required_relationship_types

        # Popola effects_on_needs per l'iniziatore (il target viene gestito in on_finish)
        self.effects_on_needs: Dict[NeedType, float] = {
            NeedType.INTIMACY: self.initiator_intimacy_gain
            # Potrebbe influenzare anche FUN o stress negativamente/positivamente
        }
        
        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} INIT - {self.npc.name}] Creata con target {self.target_npc.name}. "
                f"Durata: {self.duration_ticks}t, InitGain: {self.initiator_intimacy_gain:.1f}, "
                f"TargetGain: {self.target_intimacy_gain:.1f}, RelGain: {self.relationship_score_gain}")

    def is_valid(self) -> bool:
        # La tua logica di validazione esistente è un buon punto di partenza.
        # Ora dovrebbe usare i parametri iniettati o gli attributi dell'NPC/target,
        # invece di leggere soglie o tipi di relazione validi da 'settings' qui dentro,
        # a meno che non siano controlli molto generici.
        # Il controllo di 'consenso' (TODO VII.1.d.ii originale) sarebbe cruciale qui.

        if not super().is_valid(): return False # Controlli base
        if not self.npc or not self.target_npc or self.npc == self.target_npc:
            if settings.DEBUG_MODE and self.npc: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] NPC o Target non validi/uguali.")
            return False

        # Esempio di controllo del bisogno dell'iniziatore (la soglia potrebbe essere iniettata)
        initiator_intimacy = self.npc.get_need_value(NeedType.INTIMACY)
        intimacy_desire_threshold = getattr(settings, 'INTIMACY_ACTION_INITIATOR_DESIRE_THRESHOLD', 50.0) # Esempio soglia
        if initiator_intimacy is None or initiator_intimacy >= intimacy_desire_threshold:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Bisogno INTIMACY ({initiator_intimacy}) non abbastanza basso.")
            return False
            
        # Controlli sul target (occupato, dormendo)
        if self.target_npc.is_busy and (not self.target_npc.current_action or not self.target_npc.current_action.is_interruptible):
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} è occupato (non interrompibile).")
            return False
        if self.target_npc.current_action and self.target_npc.current_action.action_type_enum == ActionType.ACTION_SLEEP:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Target {self.target_npc.name} sta dormendo.")
            return False
            
        # Controllo del tipo di relazione e punteggio (le soglie/tipi validi potrebbero essere iniettati)
        relationship = self.npc.get_relationship_with(self.target_npc.npc_id)
        if not relationship:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Nessuna relazione con {self.target_npc.name}.")
            return False
        
        # I tipi di relazione validi e il punteggio minimo dovrebbero essere passati come config
        # Esempio: if relationship.type not in self.required_relationship_types: ...
        # Esempio: if relationship.score < self.min_required_score: ...
        # Per ora, replico la tua logica con getattr da settings:
        valid_relationship_types = { RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE }
        if relationship.type not in valid_relationship_types: # Assumendo che RelationshipInfo abbia .type
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Relazione con {self.target_npc.name} non idonea ({relationship.type.name}).")
            return False
        
        min_score = getattr(settings, "INTIMACY_ACTION_MIN_REL_SCORE", 30)
        if relationship.score < min_score: # Assumendo RelationshipInfo abbia .score
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Punteggio relazione ({relationship.score}) < {min_score}.")
            return False

        # TODO: Logica di Consenso (VII.1.d.ii) - cruciale!
        # Il target deve acconsentire. Questo potrebbe essere un check preliminare
        # o parte dell'azione (es. un'azione ProposeIntimacy che, se ha successo, accoda EngageIntimacyAction).
        # Al momento la tua SocializeAction(interaction_type=PROPOSE_INTIMACY) gestisce la proposta.
        # Questa EngageIntimacyAction dovrebbe essere triggerata solo DOPO un consenso.
        if hasattr(self.npc, 'pending_intimacy_target_accepted') and \
           self.npc.pending_intimacy_target_accepted != self.target_npc.npc_id:
            if settings.DEBUG_MODE: print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Intimità non accettata esplicitamente da {self.target_npc.name}.")
            return False


        if settings.DEBUG_MODE:
            print(f"    [{self.action_type_name} VALIDATE - {self.npc.name}] Azione con {self.target_npc.name} considerata valida.")
        return True

    def on_start(self):
        super().on_start()
        # Occupa anche il target
        if self.target_npc:
            self.target_npc.is_busy = True
            self.target_npc.current_action = self 
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} START - {self.npc.name}] Inizia intimità con {self.target_npc.name}. Target reso occupato.")
        # Resetta il flag di accettazione una volta che l'azione inizia
        if hasattr(self.npc, 'pending_intimacy_target_accepted'):
            self.npc.pending_intimacy_target_accepted = None


    # execute_tick da BaseAction

    def on_finish(self):
        # Applica effetti ai bisogni dell'iniziatore (già in self.effects_on_needs)
        # e al target, e aggiorna la relazione.
        if self.npc and self.target_npc: 
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - {self.npc.name}] Intimità con {self.target_npc.name} terminata.")
            
            self.npc.change_need_value(NeedType.INTIMACY, self.initiator_intimacy_gain)
            self.target_npc.change_need_value(NeedType.INTIMACY, self.target_intimacy_gain)
            
            effective_rel_gain = self.relationship_score_gain
            # ... (la tua logica per bonus relazione se partner etc. può rimanere qui, usando self.relationship_score_gain) ...
            current_relationship_npc_pov = self.npc.get_relationship_with(self.target_npc.npc_id)
            rel_type_to_set = RelationshipType.ROMANTIC_PARTNER 
            if current_relationship_npc_pov and current_relationship_npc_pov.type in {RelationshipType.ROMANTIC_PARTNER, RelationshipType.SPOUSE}:
                rel_type_to_set = current_relationship_npc_pov.type
                bonus_rel_gain_partner = getattr(settings, "INTIMACY_REL_GAIN_BONUS_PARTNER", 5)
                effective_rel_gain += bonus_rel_gain_partner

            self.npc.update_relationship(
                target_npc_id=self.target_npc.npc_id,
                new_type=rel_type_to_set, # O un tipo più specifico se determinato
                score_change=int(effective_rel_gain)
            )
            self.target_npc.update_relationship(
                target_npc_id=self.npc.npc_id,
                new_type=rel_type_to_set,
                score_change=int(effective_rel_gain)
            )
        
        super().on_finish() 
        
        # Libera il target NPC
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None 
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} FINISH - Target {self.target_npc.name}] Liberato.")


    def on_interrupt_effects(self):
        super().on_interrupt_effects()
        # Applica effetti parziali ai bisogni se interrotta
        if self.npc and self.target_npc and self.duration_ticks > 0:
            proportion_completed = self.elapsed_ticks / self.duration_ticks
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - {self.npc.name}] Azione intimità interrotta. Applico effetti parziali.")
            
            self.npc.change_need_value(NeedType.INTIMACY, self.initiator_intimacy_gain * proportion_completed)
            self.target_npc.change_need_value(NeedType.INTIMACY, self.target_intimacy_gain * proportion_completed)
            # Applica cambio relazione parziale? Potrebbe essere complicato o indesiderato.
            # Per ora, non applichiamo cambio relazione parziale.
        
        # Libera il target NPC anche in caso di interruzione
        if self.target_npc:
            self.target_npc.is_busy = False
            self.target_npc.current_action = None
            if settings.DEBUG_MODE:
                print(f"    [{self.action_type_name} CANCEL - Target {self.target_npc.name}] Liberato.")