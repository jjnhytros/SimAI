# core/enums/genders.py
"""
Definizione dell'Enum 'Gender' per rappresentare il genere degli NPC in SimAI.
"""
from enum import Enum, auto

class Gender(Enum):
    """
    Rappresenta il genere di un NPC.
    Basato su TODO IV.3.j.i.1.
    Ulteriori opzioni come PREFER_NOT_TO_SAY o CUSTOM potrebbero essere aggiunte.
    """
    MALE = auto()
    FEMALE = auto()
    NON_BINARY = auto()
    # PREFER_NOT_TO_SAY = auto() # Opzione futura
    # CUSTOM = auto()            # Opzione futura (potrebbe richiedere un campo extra per i pronomi)

    def display_name_it(self) -> str:
        """Restituisce il nome del genere in italiano (esempio)."""
        mapping = {
            Gender.MALE: "Maschio",
            Gender.FEMALE: "Femmina",
            Gender.NON_BINARY: "Non Binario"
        }
        return mapping.get(self, self.name.replace("_", " ").title())