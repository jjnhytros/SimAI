# core/modules/moodlets/moodlet_manager.py
from typing import Dict, Optional, TYPE_CHECKING
from core.enums import MoodletType
from .moodlet_definitions import Moodlet

if TYPE_CHECKING:
    from core.character import Character

class MoodletManager:
    """Gestisce i Moodlet attivi per un singolo NPC."""
    def __init__(self, owner_npc: 'Character'):
        self.owner_npc: 'Character' = owner_npc
        # Usiamo un dizionario per evitare moodlet duplicati dello stesso tipo
        self.active_moodlets: Dict[MoodletType, Moodlet] = {}

    def add_moodlet(self, moodlet: Moodlet):
        """Aggiunge un moodlet, sovrascrivendo quello dello stesso tipo se già presente."""
        self.active_moodlets[moodlet.moodlet_type] = moodlet

    def remove_moodlet(self, moodlet_type: MoodletType):
        """Rimuove un moodlet se presente."""
        if moodlet_type in self.active_moodlets:
            del self.active_moodlets[moodlet_type]

    def has_moodlet(self, moodlet_type: MoodletType) -> bool:
        """Controlla se un moodlet di un certo tipo è attivo."""
        return moodlet_type in self.active_moodlets

    def get_total_emotional_impact(self) -> int:
        """
        Calcola e restituisce la somma degli impatti emotivi di tutti i moodlet attivi.
        Questo rappresenta l'umore generale dell'NPC.
        """
        if not self.active_moodlets:
            return 0 # Umore neutro se non ci sono moodlet
            
        total_impact = 0
        for moodlet in self.active_moodlets.values():
            total_impact += moodlet.emotional_impact
            
        return total_impact
