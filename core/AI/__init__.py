"""
Coordinatore centrale per i sistemi AI
"""
from .decision_system import DecisionSystem
from .needs_processor import NeedsProcessor
from .action_executor import ActionExecutor
from .social_manager import SocialManager

class AICoordinator:
    def __init__(self, simulation):
        self.simulation = simulation
        self.decision_system = DecisionSystem()
        self.needs_processor = NeedsProcessor()
        self.action_executor = ActionExecutor()
        self.social_manager = SocialManager()
        self.learning_system = LearningSystem()
        
    def update_all_npcs(self, time_delta):
        # Processo a livelli di dettaglio (LOD)
        for npc in self.simulation.npcs:
            if npc.lod == LOD.HIGH:
                self.update_npc_high_detail(npc, time_delta)
            else:
                self.update_npc_background(npc, time_delta)
    
    def update_npc_high_detail(self, npc, time_delta):
        # 1. Aggiornamento bisogni
        self.needs_processor.update_needs(npc, time_delta)
        
        # 2. Decisione azione
        action = self.decision_system.decide_next_action(npc, self.simulation)
        
        # 3. Esecuzione azione
        self.action_executor.execute_action(npc, action, time_delta)
        
        # 4. Apprendimento
        self.learning_system.process_learning(npc, time_delta)
        
        # 5. Interazioni sociali
        self.social_manager.handle_social_interactions(npc, self.simulation)
    
    def update_npc_background(self, npc, time_delta):
        # Versione semplificata per NPC non visibili
        self.needs_processor.update_background_needs(npc, time_delta)
        self.social_manager.update_background_relationships(npc, time_delta)