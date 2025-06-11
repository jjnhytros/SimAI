from typing import Any, Dict, Optional
from ..base_trait import BaseTrait
from core.enums import TraitType

class PartyAnimalTrait(BaseTrait):
    trait_type = TraitType.PARTY_ANIMAL
    def __init__(self, character_owner):
        super().__init__(character_owner, self.trait_type)
        self.display_name = "Animale da Festa"
        self.description = "Ama le feste, la musica alta e stare in mezzo alla gente."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene aggiunto
        return None
        
    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        # Per ora questo tratto non ha effetti speciali quando viene rimosso
        return None
