# core/modules/traits/social/loner_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait # Importa BaseTrait dalla directory genitore ('traits')

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType # Se usato

class LonerTrait(BaseTrait):
    # Il costruttore ora accetta 'trait_type' e lo passa a super()
    def __init__(self, character_owner: 'Character', trait_type: TraitType = TraitType.LONER):
        super().__init__(character_owner, trait_type)
        # display_name è già impostato da BaseTrait usando trait_type.display_name_it()
        # Puoi sovrascriverlo qui se necessario, o aggiungere una descrizione più specifica.
        # self.display_name = "Solitario" # Già gestito da Enum e BaseTrait
        self.description = "Questo NPC preferisce la propria compagnia e trova le grandi folle stancanti."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Esempio: potrebbe influenzare il decadimento del bisogno SOCIALE
        return None # Da definire

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio di come potrebbe influenzare i bisogni o le azioni:
    # def get_need_decay_modifier(self, need_type: 'NeedType') -> float:
    #     if need_type == NeedType.SOCIAL:
    #         return 0.5  # Il bisogno sociale scende molto più lentamente
    #     return 1.0

    # def get_action_choice_priority_modifier(self, action_type: 'ActionType') -> int:
    #     if action_type == ActionType.ACTION_SOCIALIZE_LARGE_GROUP: # Esempio
    #         return -20 # Forte avversione per grandi gruppi sociali
    #     if action_type == ActionType.ACTION_READ_BOOK_ALONE: # Esempio
    #         return 10
    #     return 0