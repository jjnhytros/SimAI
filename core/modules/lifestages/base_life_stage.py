# core/modules/lifestages/base_life_stage.py
from abc import ABC
from typing import TYPE_CHECKING, Dict

from core.enums.need_types import NeedType

if TYPE_CHECKING:
    from core.character import Character

class BaseLifeStage(ABC):
    """Classe base astratta per uno stadio di vita di un NPC."""
    
    def __init__(self, character_owner: 'Character'):
        self.character_owner: 'Character' = character_owner
        self.display_name: str = "Stadio Sconosciuto"
        self.description: str = ""

    def get_need_decay_modifiers(self) -> Dict[NeedType, float]:
        """
        Restituisce un dizionario di moltiplicatori per i tassi di decadimento dei bisogni.
        Esempio: {'ENERGY': 1.2} significa che l'energia cala il 20% più velocemente.
        """
        return {}

    def on_enter_stage(self):
        """Logica da eseguire quando un NPC entra in questo stadio di vita."""
        pass