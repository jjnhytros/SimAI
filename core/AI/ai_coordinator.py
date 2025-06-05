# core/AI/ai_coordinator.py
from typing import TYPE_CHECKING, Dict, Optional
from core import settings 
from .ai_decision_maker import AIDecisionMaker # Questo dovrebbe rimanere così se AIDecisionMaker è in core/AI/
from .decision_system import DecisionSystem
from .needs_processor import NeedsProcessor
from .action_executor import ActionExecutor
from .social_manager import SocialManager

if TYPE_CHECKING:
    from core.simulation import Simulation # Questo è corretto se simulation.py è in core/
    from core.character import Character   # Questo è corretto se character.py è in core/

class AICoordinator:
    def __init__(self, simulation_context: 'Simulation'): # simulation è l'istanza di Simulation
        self.simulation_context: 'Simulation' = simulation_context
        self.decision_system = DecisionSystem()
        self.needs_processor = NeedsProcessor()
        self.action_executor = ActionExecutor()
        self.social_manager = SocialManager(self.simulation_context)
        # self.learning_system = LearningSystem()

    def update_npc_ai(self, npc: 'Character', time_delta: int): # Aggiunto time_delta se serve per update_needs
        """
        Metodo principale per aggiornare lo stato e le decisioni di un NPC.
        """
        if not npc:
            return

        # 1. Aggiorna i bisogni
        # La tua classe Character ha già npc.update_needs(time_manager, ticks_elapsed)
        # Assicurati che time_delta sia il numero corretto di tick trascorsi.
        npc.update_needs(self.simulation_context.time_manager, time_delta)

        # 2. L'AIDecisionMaker (specifico dell'NPC) sceglie un'azione
        if not npc.is_busy and not npc.action_queue:
            if npc.ai_decision_maker:
                chosen_action = npc.ai_decision_maker.decide_next_action(
                    self.simulation_context.time_manager, 
                    self.simulation_context
                )
                if chosen_action:
                    npc.add_action_to_queue(chosen_action)
        
        # 3. Character.update_action gestisce l'esecuzione dell'azione corrente dalla coda
        npc.update_action(self.simulation_context.time_manager, self.simulation_context)

    def update_all_npcs(self, time_delta: int): # time_delta è il numero di tick (1)
        # Itera sugli NPC direttamente dalla simulazione
        for npc_id, npc in self.simulation_context.npcs.items(): # Modificato per iterare sul dict
            if not npc: continue # Salta se l'NPC è None per qualche motivo

            # Assicurati che ogni NPC abbia un AIDecisionMaker
            if npc.ai_decision_maker is None:
                npc.ai_decision_maker = AIDecisionMaker(npc=npc) # Passa solo npc
                if settings.DEBUG_MODE:
                    print(f"    [AICoordinator] AIDecisionMaker creato al volo per {npc.name}")

            # Chiamiamo il metodo di update dettagliato
            self.update_npc_high_detail(npc, time_delta)

    def update_npc_high_detail(self, npc, time_delta: int):
        # 1. Aggiornamento bisogni
        # NeedsProcessor.update_needs è stato modificato per non fare nulla attivamente,
        # poiché Character.update_needs è più completo.
        # Quindi, chiamiamo direttamente Character.update_needs.
        # Character.update_needs(self, time_manager, ticks_elapsed_since_last_update)
        if hasattr(npc, 'update_needs'):
            npc.update_needs(self.simulation_context.time_manager, time_delta)

        # Per il punto IV.2.a.i (invecchiamento basato su data di nascita)
        # e la gestione del nuovo giorno, questo dovrebbe rimanere qui o essere
        # gestito centralmente da Simulation prima di chiamare update_all_npcs.
        # Per ora, lo lasciamo nella logica di Simulation._update_simulation_state prima della chiamata a AICoordinator.
        # (La logica di invecchiamento giornaliero è ancora in Simulation._update_simulation_state,
        #  ma NON è più lì dopo la modifica a _update_simulation_state in questo passaggio.
        #  Dovrebbe essere responsabilità di Character.update_needs o di AICoordinator qui)

        # Controlliamo se è un nuovo giorno per l'invecchiamento
        # Questa logica era in Simulation, la spostiamo qui per coerenza con l'aggiornamento NPC
        current_ath_time = self.simulation_context.time_manager.get_current_time()
        is_new_day = (current_ath_time.hour == 0 and
                    current_ath_time.minute() == 0 and
                    self.simulation_context.time_manager.total_ticks > 1 and # Non al primissimo tick
                    time_delta > 0) # Solo se il tempo è avanzato

        if is_new_day and hasattr(npc, '_set_age_in_days') and hasattr(npc, 'get_age_in_days'):
            npc._set_age_in_days(npc.get_age_in_days() + 1)


        # 2. Decisione e Esecuzione Azione
        # ActionExecutor.execute_action è stato modificato per non fare nulla attivamente.
        # Chiamiamo direttamente Character.update_action che contiene la logica
        # per eseguire l'azione corrente e chiamare AIDecisionMaker per una nuova azione.
        if hasattr(npc, 'update_action'):
            npc.update_action(self.simulation_context.time_manager, self.simulation_context)


        # La logica originale dell'AICoordinator (commentata per riferimento):
        # self.needs_processor.update_needs(npc, time_delta)
        # action = self.decision_system.decide_next_action(npc, self.simulation)
        # self.action_executor.execute_action(npc, action, time_delta)

        # 3. Apprendimento (Futuro)
        # self.learning_system.process_learning(npc, time_delta)

        # 4. Interazioni sociali (Futuro, SocialManager è scheletrico)
        # self.social_manager.handle_social_interactions(npc, self.simulation)
        pass

    def update_npc_background(self, npc, time_delta):
        # Versione semplificata per NPC non visibili (Futuro)
        # self.needs_processor.update_background_needs(npc, time_delta)
        # self.social_manager.update_background_relationships(npc, time_delta)
        pass