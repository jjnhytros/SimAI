# core/enums/relationship_statuses.py
from enum import Enum, auto
"""
Definizione dell'Enum 'RelationshipStatus' per rappresentare lo stato
sentimentale di un NPC in SimAI.
"""

class RelationshipStatus(Enum):
    """
    Rappresenta lo stato sentimentale attuale di un NPC.
    Riferimento TODO: VII.2.b (Tipi di relazione, questo è lo stato individuale)
    """
    SINGLE = auto()                 # Single, disponibile
    CASUALLY_DATING = auto()        # Frequenta qualcuno casualmente, potrebbe essere aperto
    IN_A_RELATIONSHIP = auto()      # In una relazione impegnata (es. fidanzato/a)
    ENGAGED = auto()                # Fidanzato/a ufficialmente (promesso/a sposo/a)
    MARRIED = auto()                # Sposato/a
    DIVORCED = auto()               # Divorziato/a
    WIDOWED = auto()                # Vedovo/a
    ITS_COMPLICATED = auto()        # È complicato
    OPEN_RELATIONSHIP = auto()      # In una relazione aperta (potrebbe essere idoneo per alcuni tipi di matching)
    # Aggiungere altri stati se necessario per la simulazione

    def display_name_it(self) -> str:
        mapping = {
            RelationshipStatus.SINGLE: "Single",
            RelationshipStatus.CASUALLY_DATING: "Frequenta qualcuno",
            RelationshipStatus.IN_A_RELATIONSHIP: "In una relazione",
            RelationshipStatus.ENGAGED: "Fidanzato/a ufficialmente",
            RelationshipStatus.MARRIED: "Sposato/a",
            RelationshipStatus.DIVORCED: "Divorziato/a",
            RelationshipStatus.WIDOWED: "Vedovo/a",
            RelationshipStatus.ITS_COMPLICATED: "È complicato",
            RelationshipStatus.OPEN_RELATIONSHIP: "In una relazione aperta"
        }
        return mapping.get(self, self.name.replace("_", " ").title())