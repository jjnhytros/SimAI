# core/enums/moodlet_types.py
from enum import Enum, auto

class MoodletType(Enum):
    """Tipi di modificatori di umore (Moodlet) che un NPC può avere."""
    # Negativi
    STARVING = auto()       # Morendo di fame (fame critica)
    HUNGRY = auto()         # Affamato (fame bassa)
    BORED = auto()          # Annoiato (divertimento basso)
    STRESSED = auto()       # Stressato (carico cognitivo alto)

    # Positivi
    SATISFIED = auto()      # Soddisfatto (bisogni alti)
    WELL_FED = auto()       # Sazio (dopo aver mangiato bene)
    ENTERTAINED = auto()    # Divertito (dopo un'attività divertente)
    HAPPY = auto()          # Felice (generico)