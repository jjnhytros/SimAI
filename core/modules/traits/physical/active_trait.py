# core/modules/traits/physical/active_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
# L'import di BaseTrait dovrebbe essere dalla sua posizione corretta
# Se BaseTrait è in core/modules/traits/base_trait.py:
from core.modules.traits.base_trait import BaseTrait 
# Se BaseTrait è in core/modules/traits/ (cartella principale dei tratti) come discusso:
# from ..base_trait import BaseTrait # Questo sarebbe from .base_trait import BaseTrait se base_trait.py fosse nella stessa dir

if TYPE_CHECKING:
    from core.character import Character

class ActiveTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.ACTIVE
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Questo NPC ama muoversi e fare attività fisica, sentendosi rinvigorito dall'esercizio."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        return {"initial_moodlet": "FEELING_ENERGETIC"} 

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # ... altri metodi specifici del tratto ...