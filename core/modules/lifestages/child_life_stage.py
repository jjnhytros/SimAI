# core/modules/lifestages/child_life_stage.py
from .base_life_stage import BaseLifeStage
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.character import Character

class ChildLifeStage(BaseLifeStage):
    """Logica e modificatori per lo stadio di vita 'Bambino'."""
    
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner)
        self.display_name = "Bambino"
        self.description = "Un periodo di apprendimento e gioco."

    def get_need_decay_modifiers(self) -> Dict[str, float]:
        # I bambini hanno bisogno di più energia e si annoiano più in fretta
        return {
            "ENERGY": 1.25, # Il 25% più veloce
            "FUN": 1.5,     # Il 50% più veloce
        }