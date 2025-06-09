# core/AI/solution_discoverers/base_discoverer.py
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.modules.memory.memory_definitions import Problem
    from core.character import Character
    from core.simulation import Simulation
    from core.modules.actions.action_base import BaseAction

class BaseSolutionDiscoverer(ABC):
    """
    Classe base astratta per le strategie che scoprono soluzioni (Azioni)
    per un dato Problema. Ogni "esperto" per un bisogno (fame, sete, etc.)
    erediterà da questa classe.
    """
    @abstractmethod
    def discover(self, problem: 'Problem', npc: 'Character', simulation_context: 'Simulation') -> List['BaseAction']:
        """
        Data un problema, un NPC e il contesto della simulazione, questo metodo
        restituisce una lista di possibili Azioni valide per risolverlo.
        """
        pass