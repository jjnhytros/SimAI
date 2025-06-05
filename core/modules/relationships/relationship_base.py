# simai/core/modules/relationships/relationship_base.py
"""
Definizione della dataclass 'Relationship' che rappresenta la struttura base
di una relazione tra due NPC in SimAI.
"""
import uuid # Useremo uuid.UUID per gli ID internamente, poi convertiti a str se necessario per le chiavi del dizionario in Character
from dataclasses import dataclass, field
from typing import Set, Optional

from core.enums import RelationshipType

@dataclass
class Relationship:
    """
    Struttura dati evoluta per una relazione unidirezionale.
    """
    target_npc_id: str # Manteniamo str per coerenza con la chiave del dizionario in Character
    
    friendship_score: int = 0   # Da -100 (nemico) a +100 (migliore amico)
    romance_score: int = 0      # Da 0 (nessun interesse) a +100 (grande amore)
    
    # Un set di RelationshipType attuali.
    # Permette, ad esempio, di essere contemporaneamente COLLEAGUE e FRIEND_REGULAR.
    current_types: Set[RelationshipType] = field(default_factory=set)
    
    # Storico dei tipi di relazione più significativi avuti (opzionale, per profondità)
    # historical_types: Set[RelationshipType] = field(default_factory=set)

    # Altri campi che potrebbero diventare utili:
    # trust_level: int = 50 # 0-100
    # respect_level: int = 50 # 0-100
    # initial_impression_score: Optional[int] = None # Per VII.2.b.iii.A
    # last_interaction_timestamp: Optional[float] = None

    def __post_init__(self):
        self.friendship_score = max(-100, min(100, self.friendship_score))
        self.romance_score = max(0, min(100, self.romance_score))
        if not self.current_types: # Se non vengono passati tipi iniziali
            self.current_types.add(RelationshipType.ACQUAINTANCE) # Default

    def update_relationship_metrics(self, friendship_delta: int = 0, romance_delta: int = 0):
        self.friendship_score = max(-100, min(100, self.friendship_score + friendship_delta))
        self.romance_score = max(0, min(100, self.romance_score + romance_delta))
        # Qui andrebbe la logica per aggiornare self.current_types in base ai nuovi punteggi
        # self._evaluate_and_set_types()

    # def _evaluate_and_set_types(self):
    #     # Esempio di logica (da definire nel dettaglio):
    #     if self.friendship_score >= 75:
    #         self.current_types.add(RelationshipType.FRIEND_CLOSE)
    #         self.current_types.discard(RelationshipType.FRIEND_REGULAR)
    #         self.current_types.discard(RelationshipType.ACQUAINTANCE)
    #     elif self.friendship_score >= 40:
    #         self.current_types.add(RelationshipType.FRIEND_REGULAR)
    #         self.current_types.discard(RelationshipType.FRIEND_CLOSE)
    #         self.current_types.discard(RelationshipType.ACQUAINTANCE)
    #     # ... e così via per gli altri tipi e punteggi, inclusi quelli negativi per ENEMY, etc.
    #     # Tipi come SPOUSE, PARENT, SIBLING sarebbero gestiti diversamente (non solo da score).
    #     pass
