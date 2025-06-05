# core/enums/skill_types.py
"""
Definizione dell'Enum 'SkillType' per rappresentare i tipi di abilità
che gli NPC possono sviluppare in SimAI.
"""
from enum import Enum, auto

class SkillType(Enum):
    # Esempi di Skill, da popolare con la tua lista completa (da TODO IX.e)
    COOKING = auto()
    LOGIC = auto()
    PROGRAMMING = auto()
    FITNESS = auto()
    CHARISMA = auto()
    HANDINESS = auto() # Manualità
    GARDENING = auto()
    WRITING = auto()
    PAINTING = auto()
    GUITAR = auto()
    PIANO = auto()
    VIOLIN = auto()
    ROCKET_SCIENCE = auto()
    PARENTING = auto()
    HERBALISM = auto()
    PHOTOGRAPHY = auto()
    BAKING = auto()
    DJ_MIXING = auto()
    ACTING = auto()
    ARCHAEOLOGY = auto()
    # ... e molte altre dalla tua lista TODO IX.e

    # Potremmo aggiungere un metodo display_name_it() come per gli altri Enum
    def display_name_it(self) -> str:
        # Semplice implementazione di esempio, da personalizzare
        return self.name.replace("_", " ").title()