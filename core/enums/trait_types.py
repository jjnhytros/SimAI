# core/enums/trait_types.py
from enum import Enum, auto
"""
Definizione dell'Enum TraitType per i tipi di tratti di personalità degli NPC.
Riferimento TODO: IV.3.b
"""

class TraitType(Enum):
    """Enum per i diversi tratti di personalità."""
    # Esempi di tratti iniziali
    AMBITIOUS = auto()          # Ambizioso
    LAZY = auto()               # Pigro
    SOCIAL = auto()             # Socievole (o Extrovert)
    LONER = auto()              # Solitario (o Introvert)
    GLUTTON = auto()            # Goloso
    FRUGAL = auto()             # Frugale
    OPTIMIST = auto()           # Ottimista
    PESSIMIST = auto()          # Pessimista
    NEAT = auto()               # Ordinato
    SLOB = auto()               # Disordinato/Sciatto
    CREATIVE = auto()           # Creativo
    LOGICAL = auto()            # Logico
    ACTIVE = auto()             # Attivo (ama lo sport/movimento)
    BOOKWORM = auto()           # Topo di biblioteca
    GOOD = auto()               # Buono (gentile, empatico)
    EVIL = auto()               # Malvagio (meschino, crudele) - da considerare con attenzione
    ROMANTIC = auto()           # Romantico
    UNFLIRTY = auto()           # Non portato per il flirt
    FAMILY_ORIENTED = auto()    # Orientato alla famiglia
    HATES_CHILDREN = auto()     # Odia i bambini
    JEALOUS = auto()            # Geloso
    LOYAL = auto()              # Leale

    # TODO: Aggiungere molti altri tratti come da TODO_04.md (IV.3.b)

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tratto."""
        # Semplice implementazione, potrebbe essere migliorata con un dizionario di traduzione
        # o integrata con il sistema i18n futuro.
        mapping = {
            TraitType.AMBITIOUS: "Ambizioso",
            TraitType.LAZY: "Pigro",
            TraitType.SOCIAL: "Socievole",
            TraitType.LONER: "Solitario",
            TraitType.GLUTTON: "Ghiottone",
            TraitType.FRUGAL: "Frugale",
            TraitType.OPTIMIST: "Ottimista",
            TraitType.PESSIMIST: "Pessimista",
            TraitType.NEAT: "Ordinato",
            TraitType.SLOB: "Disordinato",
            TraitType.CREATIVE: "Creativo",
            TraitType.LOGICAL: "Logico",
            TraitType.ACTIVE: "Attivo",
            TraitType.BOOKWORM: "Topo di Biblioteca",
            TraitType.GOOD: "Buono",
            TraitType.EVIL: "Malvagio",
            TraitType.ROMANTIC: "Romantico",
            TraitType.UNFLIRTY: "Non Ammiccante",
            TraitType.FAMILY_ORIENTED: "Orientato alla Famiglia",
            TraitType.HATES_CHILDREN: "Odia i Bambini",
            TraitType.JEALOUS: "Geloso",
            TraitType.LOYAL: "Leale",
        }
        return mapping.get(self, self.name.replace("_", " ").capitalize())
