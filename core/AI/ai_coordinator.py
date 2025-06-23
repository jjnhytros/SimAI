# core/AI/ai_coordinator.py
from typing import TYPE_CHECKING, Dict, Optional
from core import settings
from core.config.life_stage_modifiers import LifeStageEffectSystem 
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
        # La tua classe Character ha già npc.update_needs(time_manager, elapsed_ticks)
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

    def update_npc_high_detail(self, npc: 'Character', time_delta: int):
        """
        Esegue un ciclo di update completo per un NPC ad alto livello di dettaglio.
        Questo include l'aggiornamento dei bisogni e il ciclo di azione/decisione.
        
        Args:
            npc (Character): L'NPC da aggiornare.
            time_delta (int): Il numero di tick trascorsi dall'ultimo update.
        """
        if not npc:
            return

        time_manager = self.simulation_context.time_manager
        
        # Possiamo usare questa logica per triggerare eventi o controlli orari.
        # Ad esempio, resettare lo stato decisionale dell'IA ogni ora per evitare
        # che si "blocchi" se non trova un'azione valida.
        is_new_hour = False
        if time_manager:
            current_time = time_manager.get_current_time()
            # --- CORREZIONE QUI ---
            # Accediamo a .minute come attributo (un intero), non come metodo.
            if current_time.minute == 0:
                is_new_hour = True
                # Potremmo aggiungere una stampa di debug per l'ora qui se volessimo.
        
        if is_new_hour and npc.ai_decision_maker:
            # Resetta lo stato anti-ripetizione dell'IA per dargli una "nuova possibilità"
            npc.ai_decision_maker.reset_decision_state()

        LifeStageEffectSystem.apply_dynamic_effects(npc)

        # 1. Aggiorna i bisogni dell'NPC in base al tempo trascorso.
        # Questo fa decadere i bisogni e aggiorna il carico cognitivo.
        if self.simulation_context:
            npc.update_needs(self.simulation_context.time_manager, time_delta)

        # 2. Aggiorna lo stato dell'azione corrente dell'NPC.
        # Questo metodo è molto importante perché al suo interno:
        #  - Esegue il tick dell'azione in corso.
        #  - Gestisce la fine di un'azione (chiamando on_finish).
        #  - Avvia la prossima azione dalla coda se l'NPC è libero.
        #  - Chiama l'AIDecisionMaker se l'NPC è libero e la coda è vuota.
        npc.update_action(time_manager, self.simulation_context)
        # L'IA prende una nuova decisione solo se non sta già facendo qualcosa
        # e solo ogni tot di tick, per evitare calcoli inutili.
        if not npc.is_busy:
            # Usiamo un attributo di AIDecisionMaker per il cooldown
            decision_maker = npc.ai_decision_maker
            if decision_maker:
                decision_maker.ticks_since_last_decision += time_delta
                
                # Pensa a una nuova azione solo se il cooldown è scaduto
                if decision_maker.ticks_since_last_decision >= decision_maker.DECISION_COOLDOWN_TICKS:
                    decision_maker.decide_next_action(self.simulation_context.time_manager, self.simulation_context)
                    decision_maker.ticks_since_last_decision = 0 # Resetta il cooldown

    def update_npc_background(self, npc, time_delta):
        # Versione semplificata per NPC non visibili (Futuro)
        # self.needs_processor.update_background_needs(npc, time_delta)
        # self.social_manager.update_background_relationships(npc, time_delta)
        pass