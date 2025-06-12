# core/modules/traits/social/social_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.action_types import ActionType
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait # Importa BaseTrait dalla directory genitore ('traits')

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType # Se usato

class SocialTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.SOCIAL
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Ha bisogno di interagire con gli altri per essere felice."

    def get_action_choice_priority_modifier(self, action, simulation_context):
        if action.action_type_enum == ActionType.ACTION_SOCIALIZE:
            return 2.0 # Forte preferenza per le azioni sociali
        return 1.0

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Esempio: Leggero aumento del bisogno Sociale o facilità nel fare amicizia.
        return None # Da definire

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # Esempio:
    # def get_need_decay_modifier(self, need_type: 'NeedType') -> float:
    #     if need_type == NeedType.SOCIAL:
    #         # Potrebbe avere un decadimento più lento del bisogno Sociale se solo,
    #         # o un guadagno maggiore quando socializza.
    #         # Se è 'Social' e non socializza, il bisogno potrebbe scendere più velocemente.
    #         # Questo dipende da come vuoi che funzioni il tratto "Socievole".
    #         # Ad esempio, potrebbe essere:
    #         # if not self.character_owner.is_socializing(): return 1.1 # Scende più veloce se solo
    #         return 0.9 # O scende più lentamente in generale
    #     return 1.0