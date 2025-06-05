# core/modules/traits/personality/lazy_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType
    # from core.enums.action_types import ActionType

class LazyTrait(BaseTrait):
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner, TraitType.LAZY)
        self.description = "Questo NPC preferisce rilassarsi e evitare sforzi faticosi. Ama il comfort e i piaceri semplici."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        return None

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio:
    # def get_need_decay_modifier(self, need_type: 'NeedType') -> float:
    #     if need_type == NeedType.ENERGY:
    #         return 1.1 # L'energia scende un po' più velocemente, o si stanca prima
    #     return 1.0

    # def get_action_choice_priority_modifier(self, action_type: 'ActionType') -> int:
    #     if action_type == ActionType.ACTION_NAP or action_type == ActionType.ACTION_WATCH_TV: # Esempi
    #         return 15
    #     if action_type == ActionType.ACTION_WORK_HARD or action_type == ActionType.ACTION_EXERCISE: # Esempi
    #         return -10
    #     return 0