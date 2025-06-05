# core/modules/traits/lifestyle/artistic_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType

class ArtisticTrait(BaseTrait):
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner, TraitType.ARTISTIC)
        self.display_name = "Artistico"
        self.description = "Questo NPC ha un'anima creativa e apprezza l'arte in molte forme."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        return None # Da definire

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # def get_need_decay_modifier(self, need_type: 'NeedType') -> float:
    #     if need_type == NeedType.FUN and not self.character_owner.is_doing_artistic_activity():
    #         return 1.15 # Il divertimento scende più velocemente se non si dedica all'arte
    #     return 1.0