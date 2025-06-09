# core/AI/thought.py
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

from core.modules.memory.memory_definitions import Problem
from ..modules.actions import BaseAction

@dataclass
class ScoredAction:
    """Contiene un'azione candidata e il punteggio che ha ricevuto."""
    action: BaseAction
    score: float

@dataclass
class Thought:
    """
    Rappresenta il processo di pensiero completo dietro una singola decisione dell'IA.
    """
    npc_id: str
    triggering_problem: Problem # Il problema più urgente che ha avviato il processo
    
    # La lista di tutte le soluzioni che l'IA ha considerato, con i loro punteggi
    considered_solutions: List[ScoredAction] = field(default_factory=list)
    
    # La soluzione finale scelta
    chosen_solution: Optional[ScoredAction] = None
    
    # Descrizione testuale del ragionamento
    reasoning_log: str = ""

    def __str__(self) -> str:
        chosen_action_name = self.chosen_solution.action.action_type_name if self.chosen_solution else "Nessuna"
        return (f"Thought(NPC: {self.npc_id[:8]}, "
                f"Problema: {self.triggering_problem.problem_type.name}, "
                f"Opzioni: {len(self.considered_solutions)}, "
                f"Scelta: {chosen_action_name})")