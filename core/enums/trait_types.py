# core/enums/trait_types.py
from enum import Enum, auto
"""
Definizione dell'Enum TraitType per i tipi di tratti di personalità degli NPC.
Riferimento TODO: IV.3.b
"""

class TraitType(Enum):
    """Enum per i diversi tratti di personalità."""
    # Esempi di tratti iniziali
    ACTIVE = auto()             # Attivo (ama lo sport/movimento)
    AMBITIOUS = auto()          # Ambizioso
    BOOKWORM = auto()           # Topo di biblioteca
    CHARMER = auto()            # Charmante
    CONSERVATIVE = auto()       # Conservativo
    DARING = auto()             # Dardoso
    DETERMINED = auto()         # Determinato
    EMBARRASSING = auto()       # Embarrassante
    EMBRACER = auto()           # Embracante
    ENTHUSIAST = auto()         # Entusiasta
    FAMOUS = auto()             # Noto
    FAVORABLE = auto()          # Favorito
    FRIENDLY = auto()           # Amabile
    CREATIVE = auto()           # Creativo
    EVIL = auto()               # Malvagio (meschino, crudele) - da considerare con attenzione
    FAMILY_ORIENTED = auto()    # Orientato alla famiglia
    FRUGAL = auto()             # Frugale
    GLUTTON = auto()            # Goloso
    GOOD = auto()               # Buono (gentile, empatico)
    HATES_CHILDREN = auto()     # Odia i bambini
    JEALOUS = auto()            # Geloso
    LAZY = auto()               # Pigro
    LOGICAL = auto()            # Logico
    LONER = auto()              # Solitario (o Introvert)
    LOYAL = auto()              # Leale
    NEAT = auto()               # Ordinato
    OPTIMIST = auto()           # Ottimista
    PESSIMIST = auto()          # Pessimista
    ROMANTIC = auto()           # Romantico
    SHY = auto()                # Timido
    SLOB = auto()               # Disordinato/Sciatto
    SOCIAL = auto()             # Socievole (o Extrovert)
    UNFLIRTY = auto()           # Non portato per il flirt

    # TODO: Aggiungere molti altri tratti come da TODO_04.md (IV.3.b)

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tratto."""
        # Semplice implementazione, potrebbe essere migliorata con un dizionario di traduzione
        # o integrata con il sistema i18n futuro.
        mapping = {
            TraitType.ACTIVE: "Attivo",
            TraitType.AMBITIOUS: "Ambizioso",
            TraitType.BOOKWORM: "Topo di Biblioteca",
            TraitType.CREATIVE: "Creativo",
            TraitType.CHARMER: "Charmante",
            TraitType.EVIL: "Malvagio",
            TraitType.FAMILY_ORIENTED: "Orientato alla Famiglia",
            TraitType.FRUGAL: "Frugale",
            TraitType.GLUTTON: "Ghiottone",
            TraitType.GOOD: "Buono",
            TraitType.HATES_CHILDREN: "Odia i Bambini",
            TraitType.JEALOUS: "Geloso",
            TraitType.LAZY: "Pigro",
            TraitType.LOGICAL: "Logico",
            TraitType.LONER: "Solitario",
            TraitType.LOYAL: "Leale",
            TraitType.NEAT: "Ordinato",
            TraitType.OPTIMIST: "Ottimista",
            TraitType.PESSIMIST: "Pessimista",
            TraitType.ROMANTIC: "Romantico",
            TraitType.SHY: "Timido",
            TraitType.SLOB: "Disordinato",
            TraitType.SOCIAL: "Socievole",
            TraitType.UNFLIRTY: "Non Ammiccante",
        }
        return mapping.get(self, self.name.replace("_", " ").capitalize())
