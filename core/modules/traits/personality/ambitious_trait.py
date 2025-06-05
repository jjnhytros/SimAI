# core/modules/traits/personality/ambitious_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait # Importa BaseTrait dalla directory genitore

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.action_types import ActionType # Se usato

class AmbitiousTrait(BaseTrait):
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner, TraitType.AMBITIOUS)
        # display_name è già impostato da BaseTrait usando trait_type.display_name_it()
        self.description = "Questo NPC ha grandi sogni, è determinato a fare carriera e a raggiungere posizioni di prestigio."

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Potrebbe influenzare l'aspirazione iniziale o la motivazione al lavoro
        return None 

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio di come potrebbe influenzare le azioni:
    # def get_action_choice_priority_modifier(self, action_type: 'ActionType') -> int:
    #     if action_type == ActionType.ACTION_WORK_HARD: # Esempio di ActionType
    #         return 20 # Priorità più alta per lavorare sodo
    #     if action_type == ActionType.ACTION_PURSUE_HOBBY: # Esempio
    #         return -5 # Meno priorità agli hobby se interferiscono con la carriera
    #     return 0