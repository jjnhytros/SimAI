# core/enums/need_types.py
from enum import Enum, auto

from core.enums.genders import Gender
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

    def display_name_it(self, gender: 'Gender') -> str:
        """
        Restituisce un nome leggibile per il bisogno.
        La firma accetta 'gender' per coerenza, anche se la maggior parte dei nomi è invariabile.
        """
        # La maggior parte dei nomi dei bisogni in italiano sono sostantivi e invariabili
        mapping = {
            NeedType.HUNGER: "Fame",
            NeedType.THIRST: "Sete",
            NeedType.ENERGY: "Energia",
            NeedType.FUN: "Divertimento",
            NeedType.SOCIAL: "Socialità",
            NeedType.HYGIENE: "Igiene",
            NeedType.BLADDER: "Vescica",
            NeedType.INTIMACY: "Intimità",
            NeedType.STRESS: "Stress",
            NeedType.COMFORT: "Comfort",
            NeedType.ENVIRONMENT: "Ambiente",
            NeedType.SAFETY: "Sicurezza",
            NeedType.CREATIVITY: "Creatività",
            NeedType.LEARNING: "Apprendimento",
            NeedType.AUTONOMY: "Autonomia",
            NeedType.ACHIEVEMENT: "Realizzazione",
            NeedType.SPIRITUALITY: "Spiritualità",
        }
        
        # Usiamo .get() con un fallback che formatta il nome dell'enum
        return mapping.get(self, self.name.replace("_", " ").title())
