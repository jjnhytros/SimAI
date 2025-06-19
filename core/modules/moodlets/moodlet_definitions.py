# core/modules/moodlets/moodlet_definitions.py
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from core.enums import MoodletType
import time

if TYPE_CHECKING:
    from core.character import Character

@dataclass
class Moodlet:
    """
    Rappresenta un modificatore di umore temporaneo per un NPC.
    """
    owner_npc: 'Character'
    moodlet_type: MoodletType
    emotional_impact: int
    duration_ticks: int
    
    source_description: str = ""
    
    # Questo attributo viene gestito dal MoodletManager
    creation_tick: float = field(default_factory=time.time, init=False)
    
    @property
    def display_name(self) -> str:
        """Proprietà dinamica che restituisce il nome corretto per genere."""
        # Ora questa chiamata funziona perché abbiamo accesso a self.owner_npc
        return self.moodlet_type.display_name_it(self.owner_npc.gender)

    @property
    def is_positive(self) -> bool:
        return self.emotional_impact > 0