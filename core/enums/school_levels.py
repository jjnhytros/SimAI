# core/enums/school_levels.py
"""
Definizione dell'Enum 'SchoolLevel' per rappresentare i livelli di istruzione
degli NPC in SimAI, come da TODO V.1.a.i.
"""
from enum import Enum, auto

class SchoolLevel(Enum):
    """
    Rappresenta i diversi livelli di istruzione che un NPC può aver raggiunto o frequentare.
    Basato sulle specifiche in TODO V.1.a.i.
    """
    NONE = auto()                               # Nessuna istruzione formale / Non applicabile
    INFANCY_EDUCATION = auto()                  # Infanzia (1-3 anni, es. asilo nido)
    LOWER_ELEMENTARY = auto()                   # Elementari Inferiori (3/4-6 anni)
    UPPER_ELEMENTARY = auto()                   # Elementari Superiori (6/7-9 anni)
    LOWER_MIDDLE_SCHOOL = auto()                # Medie Inferiori (9/10-12 anni)
    UPPER_MIDDLE_SCHOOL = auto()                # Medie Superiori (12/13-15 anni)
    HIGH_SCHOOL = auto()                        # Superiori (15/16-18 anni, obbligatorio)
    PRE_UNIVERSITY_OPTIONAL = auto()            # Superior Facoltativo (18/19-21 anni, preparazione pre-universitaria)
    UNIVERSITY = auto()                         # Università (21+ anni, specializzazione universitaria)
                                                # (Dettagli come Laurea Triennale, Magistrale, Dottorato
                                                # saranno gestiti internamente, come da TODO V.2.h.ii)

    def display_name_it(self) -> str:
        mapping = {
            SchoolLevel.NONE: "Nessuna Istruzione Formale",
            SchoolLevel.INFANCY_EDUCATION: "Educazione Infantile (1-3 anni)",
            SchoolLevel.LOWER_ELEMENTARY: "Elementari Inferiori",
            SchoolLevel.UPPER_ELEMENTARY: "Elementari Superiori",
            SchoolLevel.LOWER_MIDDLE_SCHOOL: "Scuola Media Inferiore",
            SchoolLevel.UPPER_MIDDLE_SCHOOL: "Scuola Media Superiore",
            SchoolLevel.HIGH_SCHOOL: "Scuola Superiore (Obbligatoria)",
            SchoolLevel.PRE_UNIVERSITY_OPTIONAL: "Preparazione Pre-Universitaria (Facoltativa)",
            SchoolLevel.UNIVERSITY: "Università",
        }
        return mapping.get(self, self.name.replace("_", " ").title())

    def is_compulsory_education(self) -> bool:
        """Indica se questo livello fa parte dell'istruzione obbligatoria di Anthalys."""
        # Secondo TODO V.1.a.i ("Superiori (15/16-18 anni, obbligatorio)"),
        # potremmo considerare obbligatori i livelli fino a HIGH_SCHOOL incluso. Da confermare con il lore.
        # Esempio:
        return self in {
            SchoolLevel.LOWER_ELEMENTARY, SchoolLevel.UPPER_ELEMENTARY,
            SchoolLevel.LOWER_MIDDLE_SCHOOL, SchoolLevel.UPPER_MIDDLE_SCHOOL,
            SchoolLevel.HIGH_SCHOOL
        }
        # return False # Placeholder se la logica esatta dell'obbligo deve essere definita altrove

    def is_higher_education(self) -> bool:
        """Indica se il livello è considerato istruzione superiore terziaria."""
        return self in {SchoolLevel.UNIVERSITY, SchoolLevel.PRE_UNIVERSITY_OPTIONAL}