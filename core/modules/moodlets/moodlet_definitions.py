# core/modules/moodlets/moodlet_definitions.py
from dataclasses import dataclass, field
import time
from core.enums import MoodletType

@dataclass
class Moodlet:
    """Rappresenta un singolo modificatore di umore attivo su un NPC."""
    moodlet_type: MoodletType # Il tipo di moodlet (es. HUNGRY)
    display_name: str       # Il nome visualizzato (es. "Affamato")
    emotional_impact: int   # L'impatto sull'umore (es. -10 per negativo, +5 per positivo)
    duration_ticks: int # Durata del moodlet in tick di simulazione
    source_description: str = "" # Da cosa è stato causato (es. "Il bisogno di Fame è basso")
    
    # Questi attributi vengono gestiti dal MoodletManager
    creation_tick: float = field(default_factory=time.time, init=False)
    
    @property
    def is_positive(self) -> bool:
        return self.emotional_impact > 0
