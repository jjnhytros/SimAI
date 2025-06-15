# core/AI/thought.py
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
import time

# Importa Problem per il type hinting
from core.modules.actions.action_base import BaseAction
from core.modules.memory.memory_definitions import Problem

if TYPE_CHECKING:
    from .ai_decision_maker import ScoredAction

@dataclass
class ScoredAction:
    """
    Una semplice struttura per contenere un'azione candidata e il suo punteggio calcolato.
    """
    action: 'BaseAction'
    score: float

@dataclass
class Thought:
    """
    Rappresenta il processo di pensiero di un NPC in un dato momento,
    spiegando perché è stata scelta una determinata azione.
    """
    npc_id: str
    problem: Problem
    considered_actions: List['ScoredAction']
    chosen_action: 'ScoredAction'
    timestamp: float = field(default_factory=time.time)

    def get_thought_log(self) -> str:
        """Genera un log testuale leggibile del pensiero."""
        log = [f"\n--- 🤔 PENSIERO DI {self.npc_id} ---"]
        log.append(f"Problema: {self.problem.problem_type.name} (Urgenza: {self.problem.urgency:.2f})")
        log.append(f"Dettagli: {self.problem.details}")
        log.append("Opzioni Valutate:")
        # Ordina le azioni per la stampa, dalla migliore alla peggiore
        for scored_action in sorted(self.considered_actions, key=lambda x: x.score, reverse=True):
            log.append(f"  - {scored_action.action.action_type_name}: Score = {scored_action.score:.2f}")
        log.append(f"--> Azione Scelta: {self.chosen_action.action.action_type_name} (Score: {self.chosen_action.score:.2f})")
        log.append("----------------------------------")
        return "\n".join(log)
