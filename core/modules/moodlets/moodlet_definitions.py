# core/modules/moodlets/moodlet_definitions.py
from dataclasses import dataclass
from core.enums import MoodletType

@dataclass
class Moodlet:
    """Rappresenta un singolo modificatore di umore attivo su un NPC."""
    moodlet_type: MoodletType # Il tipo di moodlet (es. HUNGRY)
    display_name: str       # Il nome visualizzato (es. "Affamato")
    emotional_impact: int   # L'impatto sull'umore (es. -10 per negativo, +5 per positivo)
    source_description: str # Da cosa è stato causato (es. "Il bisogno di Fame è basso")