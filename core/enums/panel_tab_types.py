from enum import Enum, auto

class PanelTabType(Enum):
    BIO = auto()          # Biografia e Personalità
    NEEDS = auto()        # Bisogni
    RELATIONSHIPS = auto()# Relazioni
    SKILLS = auto()       # Abilità (per il futuro)
    INVENTORY = auto()    # Inventario (per il futuro)