from typing import Any, Dict, Optional
from ..base_trait import BaseTrait
from core.enums import TraitType

class UninhibitedTrait(BaseTrait):
    trait_type = TraitType.UNINHIBITED
    def __init__(self, character_owner):
        super().__init__(character_owner, self.trait_type)
        self.display_name = "Disinibito" # Verrà declinato correttamente da display_name_it
        self.description = "Ha pochi pudori e si sente a suo agio con il proprio corpo e quello degli altri."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene rimosso
        return None
