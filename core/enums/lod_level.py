# core/enums/lod_level.py
from enum import Enum, auto

class LODLevel(Enum):
    """Rappresenta i livelli di dettaglio per gli NPC."""
    HIGH = auto()   # Dettaglio alto, NPC completamente simulato
    MEDIUM = auto() # Dettaglio medio, simulazione semplificata (futuro)
    LOW = auto()    # Dettaglio basso, simulazione astratta/narrativa
    NONE = auto()   # Nessun dettaglio, NPC non attivo/fuori scena (futuro)