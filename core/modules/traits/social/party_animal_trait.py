from typing import TYPE_CHECKING, Any, Dict, Optional
from ..base_trait import BaseTrait
from core.enums import TraitType

if TYPE_CHECKING:
    from core.character import Character

class PartyAnimalTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.PARTY_ANIMAL
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Ama le feste, la musica alta e stare in mezzo alla gente."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene rimosso
        return None
