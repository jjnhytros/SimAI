# Proposta per un nuovo file: core/modules/memory/memory_system.py
from typing import List, Optional, Dict, Any
from .memory_definitions import Memory

class MemorySystem:
    def __init__(self, owner_npc: 'Character'):
        self.owner_npc = owner_npc
        self.memories: List[Memory] = []
        self.MAX_MEMORIES = 200 # Limite per evitare sovraccarico

    def add_memory(self, memory: Memory):
        """Aggiunge un nuovo ricordo e gestisce il limite massimo."""
        self.memories.insert(0, memory) # Aggiunge i più recenti all'inizio
        if len(self.memories) > self.MAX_MEMORIES:
            self._prune_memories() # Rimuove i ricordi meno importanti

    def get_memories_about(self, query_entities: Dict[str, Any]) -> List[Memory]:
        """
        Recupera ricordi pertinenti basati su una query.
        Esempio query: {'target_npc_id': 'npc_sara_id', 'action_type': 'FLIRT'}
        """
        relevant_memories = []
        for memory in self.memories:
            match = True
            for key, value in query_entities.items():
                if memory.related_entities.get(key) != value:
                    match = False
                    break
            if match:
                relevant_memories.append(memory)
        return relevant_memories

    def _process_memory_decay(self, current_timestamp: float):
        """
        Simula la perdita di intensità emotiva dei ricordi nel tempo.
        I ricordi con alta salienza decadono molto più lentamente.
        """
        # TODO: Logica per ridurre l'emotional_impact dei ricordi vecchi e poco salienti
        pass

    def _prune_memories(self):
        """Rimuove i ricordi meno salienti e con basso impatto emotivo."""
        # Ordina i ricordi per importanza e taglia i meno rilevanti
        self.memories.sort(key=lambda m: m.salience + abs(m.emotional_impact), reverse=True)
        self.memories = self.memories[:self.MAX_MEMORIES]