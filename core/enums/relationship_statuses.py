# core/enums/relationship_statuses.py
from enum import Enum, auto

from core.enums.genders import Gender
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

    def display_name_it(self, gender: Gender) -> str:
        """Restituisce un nome leggibile e declinato per lo stato sentimentale."""
        mapping = {
            # --- Declinabili ---
            RelationshipStatus.ENGAGED: {Gender.MALE: "Fidanzato Ufficialmente", Gender.FEMALE: "Fidanzata Ufficialmente"},
            RelationshipStatus.MARRIED: {Gender.MALE: "Sposato", Gender.FEMALE: "Sposata"},
            RelationshipStatus.DIVORCED: {Gender.MALE: "Divorziato", Gender.FEMALE: "Divorziata"},
            RelationshipStatus.WIDOWED: {Gender.MALE: "Vedovo", Gender.FEMALE: "Vedova"},

            # --- Invariabili ---
            RelationshipStatus.SINGLE: "Single",
            RelationshipStatus.CASUALLY_DATING: "Frequenta Qualcuno",
            RelationshipStatus.IN_A_RELATIONSHIP: "In una Relazione",
            RelationshipStatus.ITS_COMPLICATED: "È Complicato",
            RelationshipStatus.OPEN_RELATIONSHIP: "In una Relazione Aperta",
        }
        
        value = mapping.get(self)

        if isinstance(value, dict):
            # Usa il maschile come fallback
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            return value
        else:
            return self.name.replace("_", " ").title()
