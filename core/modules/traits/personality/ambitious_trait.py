# core/modules/traits/personality/ambitious_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.action_types import ActionType
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait # Importa BaseTrait dalla directory genitore

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.action_types import ActionType # Se usato

class AmbitiousTrait(BaseTrait):
    
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.AMBITIOUS
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Questo NPC è determinato a raggiungere la vetta della sua carriera."

    def get_action_choice_priority_modifier(self, action, simulation_context):
        if action.action_type_enum == ActionType.ACTION_WORK_HARD: # Ipotetica azione futura
            return 2.0
        return 1.0

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