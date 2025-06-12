from typing import TYPE_CHECKING, Any, Dict, Optional
from core.enums import TraitType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class UninhibitedTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.CHILDISH
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Ha pochi pudori e si sente a suo agio con il proprio corpo e quello degli altri."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene rimosso
        return None
