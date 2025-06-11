# core/modules/traits/creative/creative_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType

class CreativeTrait(BaseTrait):
    trait_type = TraitType.CREATIVE
    
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner=character_owner, trait_type=TraitType.CREATIVE)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Questo NPC ha una mente fertile e un bisogno innato di creare."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Potrebbe dare un piccolo boost iniziale a skill come Pittura, Scrittura, Musica
        return None

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio:
    # def get_need_decay_modifier(self, need_type: 'NeedType') -> float:
    #     if need_type == NeedType.FUN and not self.character_owner.is_doing_creative_activity():
    #         return 1.2 # Il divertimento scende molto più velocemente se non crea
    #     if need_type == NeedType.CREATIVITY: # Assumendo esista questo bisogno
    #         return 0.7 # Si sente soddisfatto più a lungo se è creativo
    #     return 1.0