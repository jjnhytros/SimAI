# core/modules/memory/memory_system.py
"""
Definisce la classe MemorySystem, il gestore dei ricordi di un NPC.
Ogni NPC avrà una propria istanza di questo sistema.
"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING

# Importa la definizione di un singolo ricordo
from .memory_definitions import Memory
from core import settings # Per leggere le configurazioni

if TYPE_CHECKING:
    from core.character import Character

class MemorySystem:
    """
    Gestisce la collezione di ricordi per un singolo NPC.
    Si occupa di aggiungere, recuperare e far decadere i ricordi.
    """
    def __init__(self, owner_npc: 'Character'):
        """
        Inizializza il sistema di memoria per un NPC specifico.

        Args:
            owner_npc (Character): Il proprietario di questo sistema di memoria.
        """
        self.owner_npc: 'Character' = owner_npc
        self.memories: List[Memory] = []
        
        # Carica il limite massimo di ricordi dal file di configurazione
        self.MAX_MEMORIES: int = getattr(settings, 'MEMORY_SYSTEM_MAX_MEMORIES', 200)

    def add_memory(self, memory: Memory):
        """Aggiunge un nuovo ricordo e gestisce il limite massimo."""
        self.memories.insert(0, memory) # Aggiunge i più recenti all'inizio
        
        if settings.DEBUG_MODE:
            print(f"    [MemorySystem - {self.owner_npc.name}] Nuovo ricordo aggiunto: {memory}")
            
        if len(self.memories) > self.MAX_MEMORIES:
            self._prune_memories()

    def get_memories_about(self, query_entities: Dict[str, Any]) -> List[Memory]:
        """
        Recupera una lista di ricordi pertinenti basati su una query.
        La query è un dizionario di entità da confrontare.
        Restituisce i ricordi in ordine cronologico (dal più recente al più vecchio).
        
        Esempio query: {'target_npc_id': 'sara_id', 'interaction_type': SocialInteractionType.FLIRT}
        """
        relevant_memories = []
        for memory in self.memories: # self.memories è già ordinato dal più recente
            # Controlla se tutte le chiavi/valori della query corrispondono a quelli del ricordo
            if all(memory.related_entities.get(key) == value for key, value in query_entities.items()):
                relevant_memories.append(memory)
        
        return relevant_memories

    def _process_memory_decay(self, current_timestamp: float):
        """
        Simula la perdita di intensità emotiva dei ricordi nel tempo.
        I ricordi con alta salienza decadono molto più lentamente.
        Questo metodo dovrebbe essere chiamato periodicamente (es. ogni ora di gioco).
        """
        decay_rate = getattr(settings, 'MEMORY_DECAY_RATE', 0.001)
        for memory in self.memories:
            time_elapsed = current_timestamp - memory.timestamp
            
            # La salienza del ricordo riduce il decadimento
            # Un ricordo con salienza 1.0 decade molto lentamente, con 0.0 decade normalmente
            actual_decay_rate = decay_rate * (1.0 - memory.salience)
            
            # Riduci l'impatto emotivo verso lo zero (neutro)
            if memory.emotional_impact > 0:
                memory.emotional_impact = max(0, memory.emotional_impact - (time_elapsed * actual_decay_rate))
            elif memory.emotional_impact < 0:
                 memory.emotional_impact = min(0, memory.emotional_impact + (time_elapsed * actual_decay_rate))


    def _prune_memories(self):
        """
        Rimuove i ricordi in eccesso, tenendo quelli più importanti.
        L'importanza è una combinazione di salienza e intensità emotiva.
        """
        # Ordina i ricordi per importanza decrescente
        self.memories.sort(key=lambda m: m.salience + abs(m.emotional_impact), reverse=True)
        
        # Mantieni solo i ricordi entro il limite massimo
        self.memories = self.memories[:self.MAX_MEMORIES]
        
        if settings.DEBUG_MODE:
            print(f"    [MemorySystem - {self.owner_npc.name}] Eseguita potatura. Ricordi rimasti: {len(self.memories)}")

    def __repr__(self) -> str:
        return f"MemorySystem(Owner: {self.owner_npc.name}, Ricordi: {len(self.memories)})"