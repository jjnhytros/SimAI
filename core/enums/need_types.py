# core/enums/need_types.py
from enum import Enum, auto
"""
Definizione dell'Enum 'NeedType' per rappresentare i bisogni fondamentali
degli NPC in SimAI.
"""

class NeedType(Enum):
    """
    Rappresenta i diversi tipi di bisogni che un NPC deve soddisfare.
    Riferimento TODO: IV.1.a, IV.1.e
    """
    # Bisogni Primari / Fisiologici
    ENERGY = auto()         # Energia / Sonno / Stanchezza
    HUNGER = auto()         # Fame
    THIRST = auto()         # Sete
    BLADDER = auto()        # Bisogno fisiologico (vescica)
    HYGIENE = auto()        # Igiene personale
    
    # Bisogni Mentali / Emotivi
    FUN = auto()            # Divertimento
    SOCIAL = auto()         # Socialità
    INTIMACY = auto()       # Intimità (non solo sessuale, ma anche affettiva)
    STRESS = auto()         # Livello di Stress (un bisogno inverso)
    
    # Bisogni Secondari / di "Alto Livello"
    COMFORT = auto()        # Comfort (ambientale, fisico)
    ENVIRONMENT = auto()    # Qualità dell'Ambiente circostante (pulizia, estetica)
    SAFETY = auto()         # Sicurezza (fisica, emotiva, finanziaria)
    CREATIVITY = auto()     # Creatività (espressione di sé, fare/creare)
    LEARNING = auto()       # Apprendimento (conoscenza, crescita personale)
    AUTONOMY = auto()       # Autonomia (senso di controllo, libertà di scelta) TODO IV.1.e.vii
    ACHIEVEMENT = auto()    # Realizzazione (senso di competenza, progresso) TODO IV.1.e.viii
    SPIRITUALITY = auto()   # Spiritualità (significato, scopo, connessione)

    # COMPETENCE = auto()# Competenza/Realizzazione (diverso da Aspirazione)
    # BELONGING è coperto da SOCIAL, ma potremmo specificarlo se necessario
    # SELF_ESTEEM è un concetto più alto, potrebbe derivare dal soddisfacimento di altri

    def display_name_it(self) -> str:
        mapping = {
            NeedType.HUNGER: "Fame",
            NeedType.BLADDER: "Vescica",
            NeedType.HYGIENE: "Igiene",
            NeedType.ENERGY: "Energia",
            NeedType.FUN: "Divertimento",
            NeedType.SOCIAL: "Sociale",
            NeedType.INTIMACY: "Intimità",
            NeedType.THIRST: "Sete",
            NeedType.COMFORT: "Comfort",
            NeedType.ENVIRONMENT: "Ambiente",
            NeedType.SAFETY: "Sicurezza",
            NeedType.CREATIVITY: "Creatività",
            NeedType.LEARNING: "Apprendimento",
            NeedType.SPIRITUALITY: "Spiritualità",
            NeedType.AUTONOMY: "Autonomia",
            NeedType.ACHIEVEMENT: "Realizzazione",
        }
        return mapping.get(self, self.name.replace("_", " ").title())