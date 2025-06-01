"""
Sistema di decisione basato su Utility AI
"""
from enum import Enum
import random

class DecisionType(Enum):
    PHYSICAL_NEED = 1
    SOCIAL_NEED = 2
    LEISURE = 3
    WORK = 4
    LEARNING = 5

class DecisionSystem:
    def decide_next_action(self, npc, simulation):
        # Calcola l'urgenza di ogni categoria di bisogni
        need_scores = self._calculate_need_scores(npc)
        
        # Applica modificatori da tratti
        self._apply_trait_modifiers(npc, need_scores)
        
        # Seleziona la categoria più urgente
        decision_type = self._select_decision_type(need_scores)
        
        # Trova azioni concrete nella categoria selezionata
        return self._select_concrete_action(npc, decision_type, simulation)
    
    def _calculate_need_scores(self, npc):
        """Calcola i punteggi di urgenza per ogni categoria"""
        # Implementazione basata sui bisogni correnti dell'NPC
        return {
            DecisionType.PHYSICAL_NEED: max(
                npc.needs.hunger, 
                npc.needs.energy, 
                npc.needs.hygiene
            ),
            # ... altre categorie
        }
    
    def _apply_trait_modifiers(self, npc, need_scores):
        """Modifica i punteggi basandosi sui tratti"""
        if "Ambitious" in npc.traits:
            need_scores[DecisionType.WORK] *= 1.3
        if "Lazy" in npc.traits:
            need_scores[DecisionType.WORK] *= 0.7
    
    def _select_decision_type(self, need_scores):
        """Seleziona il tipo di decisione con score più alto"""
        return max(need_scores, key=need_scores.get)
    
    def _select_concrete_action(self, npc, decision_type, simulation):
        """Seleziona un'azione specifica nel contesto"""
        if decision_type == DecisionType.PHYSICAL_NEED:
            return self._handle_physical_need(npc, simulation)
        # ... altri tipi
        
    def _handle_physical_need(self, npc, simulation):
        """Seleziona azione per bisogni fisici"""
        # Implementazione dettagliata con accesso al mondo
        if npc.needs.hunger < settings.NEED_CRITICAL_THRESHOLD:
            return self._find_food_action(npc, simulation)
        # ... altri bisogni fisici