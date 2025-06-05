# core/modules/traits/lifestyle/bookworm_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait # L'import di BaseTrait dalla directory genitore

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType # Se usato

class BookwormTrait(BaseTrait):
    # Il costruttore ora accetta 'trait_type' e lo passa a super()
    def __init__(self, character_owner: 'Character', trait_type: TraitType = TraitType.BOOKWORM):
        super().__init__(character_owner, trait_type)
        # display_name e description possono essere ulteriormente personalizzati qui se necessario,
        # altrimenti useranno quelli impostati da BaseTrait basati su trait_type.display_name_it().
        # self.display_name = "Topo di Biblioteca" # Opzionale, se vuoi sovrascrivere quello dell'enum
        self.description = "Questo NPC adora leggere e immergersi nei libri."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Esempio: Aumenta il bisogno FUN quando legge, o la velocità di apprendimento da libri
        return {"initial_moodlet": "HAPPY_TO_READ"} # Esempio

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio di influenza sulle azioni o sui bisogni
    # def get_action_choice_priority_modifier(self, action_type: 'ActionType') -> int:
    #     if action_type == ActionType.ACTION_READ_BOOK: # Assumendo esista questa ActionType
    #         return 20 # Alta priorità per leggere
    #     return 0

    # def get_fun_satisfaction_modifier(self, action_type: 'ActionType', base_fun_gain: float) -> float:
    #     if action_type == ActionType.ACTION_READ_BOOK:
    #         return base_fun_gain * 1.5 # Ottiene più divertimento dalla lettura
    #     return base_fun_gain