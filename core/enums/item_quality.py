# core/enums/item_quality.py
from enum import Enum, auto

class ItemQuality(Enum):
    """Rappresenta la qualità di un oggetto creato da un NPC."""
    POOR = auto()           # Scadente
    NORMAL = auto()         # Normale
    GOOD = auto()           # Buono
    EXCELLENT = auto()      # Eccellente
    MASTERPIECE = auto()    # Capolavoro