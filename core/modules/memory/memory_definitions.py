# core/modules/memory/memory_definitions.py
"""
Definisce la dataclass Memory, che rappresenta un singolo ricordo.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid

@dataclass
class Memory:
    """
    Rappresenta un singolo ricordo significativo per un NPC.
    """
    # --- Campi Obbligatori (Senza Valore di Default) ---
    npc_id: str                 # ID dell'NPC che possiede questo ricordo
    event_description: str      # Stringa leggibile per il debug
    emotional_impact: float     # Impatto emotivo (da -1.0 a 1.0)
    salience: float             # Importanza del ricordo (da 0.0 a 1.0)
    timestamp: float            # Tick della simulazione in cui è avvenuto

    # --- Campi con Valore di Default ---
    memory_id: uuid.UUID = field(default_factory=uuid.uuid4)
    related_entities: Dict[str, Any] = field(default_factory=dict)

    def get_emotional_impact_modifier(self) -> float:
        """Restituisce un modificatore di punteggio basato sull'impatto emotivo."""
        return 1.0 + self.emotional_impact

    def __repr__(self) -> str:
        return (f"Memory(Owner: {self.npc_id[:8]}, Desc: '{self.event_description}', "
                f"Impact: {self.emotional_impact:.2f}, Salience: {self.salience:.2f})")