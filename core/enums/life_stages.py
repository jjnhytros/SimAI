# core/enums/life_stages.py
"""
Definizione dell'Enum 'LifeStage' per rappresentare le fasi della vita
degli NPC in SimAI.
"""
from enum import Enum, auto

class LifeStage(Enum):
    """
    Rappresenta le diverse fasi della vita di un NPC.
    Le soglie di età per ogni fase sono definite in settings.LIFE_STAGE_AGE_THRESHOLDS_DAYS.
    Riferimento Lore: "Le Fasi della Vita e le Tradizioni di Anthalys"
    Riferimento TODO: IV.2.d
    """
    INFANCY = auto()            # Infanzia (0-1 anno)
    TODDLERHOOD = auto()        # Prima Fanciullezza (1-3 anni)
    EARLY_CHILDHOOD = auto()    # Fanciullezza Media / Preschool (3-5 anni)
    MIDDLE_CHILDHOOD = auto()   # Tarda Fanciullezza (6-11 anni)
    ADOLESCENCE = auto()        # Adolescenza (12-19 anni)
    EARLY_ADULTHOOD = auto()    # Prima Età Adulta (20-39 anni)
    MIDDLE_ADULTHOOD = auto()   # Età Adulta Media (40-59 anni)
    LATE_ADULTHOOD = auto()     # Tarda Età Adulta (60-79 anni)
    ELDERLY = auto()            # Anzianità (80+ anni)

    def display_name_it(self) -> str:
        """Restituisce il nome della fase della vita in italiano."""
        # Questo mapping può essere espanso o gestito diversamente se necessario.
        # Per ora, usiamo i nomi italiani che hai fornito nella lore.
        mapping = {
            LifeStage.INFANCY: "Infanzia",
            LifeStage.TODDLERHOOD: "Prima Fanciullezza",
            LifeStage.EARLY_CHILDHOOD: "Fanciullezza Media", # (o Età Prescolare)
            LifeStage.MIDDLE_CHILDHOOD: "Tarda Fanciullezza",
            LifeStage.ADOLESCENCE: "Adolescenza",
            LifeStage.EARLY_ADULTHOOD: "Prima Età Adulta",
            LifeStage.MIDDLE_ADULTHOOD: "Età Adulta Media",
            LifeStage.LATE_ADULTHOOD: "Tarda Età Adulta",
            LifeStage.ELDERLY: "Anzianità"
        }
        return mapping.get(self, self.name.replace("_", " ").title())