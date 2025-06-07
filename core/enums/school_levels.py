# core/enums/school_levels.py
from enum import Enum, auto
"""
Definizione dell'Enum SchoolLevel per i livelli di istruzione in SimAI.
Riferimento TODO: Sezione V
"""

class SchoolLevel(Enum):
    """
    Rappresenta i diversi livelli del sistema scolastico di Anthalys.
    """
    NONE = auto()                   # Non iscritto / Ha terminato / Non applicabile

    # Ciclo Prescolare
    INFANCY_SCHOOL = auto()         # Scuola dell'Infanzia (1-3 anni)
    
    # Scuole Elementari
    LOWER_ELEMENTARY = auto()       # Elementari Inferiori (3/4-6 anni)
    UPPER_ELEMENTARY = auto()       # Elementari Superiori (6/7-9 anni)

    # Scuole Medie
    LOWER_MIDDLE_SCHOOL = auto()    # Medie Inferiori (9/10-12 anni)
    UPPER_MIDDLE_SCHOOL = auto()    # Medie Superiori (12/13-15 anni)

    # Scuole Superiori
    HIGH_SCHOOL = auto()            # Superiori (15/16-18 anni) - Istruzione Obbligatoria
    PRE_UNIVERSITY = auto()         # Superior Facoltativo (18/19-21 anni) - Preparazione Universitaria
    
    # Istruzione Superiore
    UNIVERSITY = auto()             # Università (21+ anni)

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il livello scolastico."""
        mapping = {
            SchoolLevel.NONE: "Nessuna Istruzione",
            SchoolLevel.INFANCY_SCHOOL: "Scuola dell'Infanzia",
            SchoolLevel.LOWER_ELEMENTARY: "Elementari Inferiori",
            SchoolLevel.UPPER_ELEMENTARY: "Elementari Superiori",
            SchoolLevel.LOWER_MIDDLE_SCHOOL: "Medie Inferiori",
            SchoolLevel.UPPER_MIDDLE_SCHOOL: "Medie Superiori",
            SchoolLevel.HIGH_SCHOOL: "Scuole Superiori",
            SchoolLevel.PRE_UNIVERSITY: "Corso Pre-Universitario",
            SchoolLevel.UNIVERSITY: "Università",
        }
        return mapping.get(self, self.name.replace("_", " ").title())

    @property
    def is_compulsory(self) -> bool:
        """
        Restituisce True se questo livello scolastico è parte dell'istruzione obbligatoria.
        Basato su TODO V.2.f (Superiori obbligatorie).
        """
        # Puoi espandere questo set se altri livelli diventano obbligatori
        return self in {
            SchoolLevel.LOWER_ELEMENTARY,
            SchoolLevel.UPPER_ELEMENTARY,
            SchoolLevel.LOWER_MIDDLE_SCHOOL,
            SchoolLevel.UPPER_MIDDLE_SCHOOL,
            SchoolLevel.HIGH_SCHOOL,
        }
