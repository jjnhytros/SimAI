# core/modules/traits/social/social_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait # Importa BaseTrait dalla directory genitore ('traits')

if TYPE_CHECKING:
    from core.character import Character
    # from core.enums.need_types import NeedType # Se usato

class SocialTrait(BaseTrait):
    # Il costruttore ora accetta 'trait_type' e lo passa a super()
    # Forniamo un default per trait_type se la classe dovesse mai essere istanziata direttamente
    # senza che _initialize_traits fornisca il tipo esatto.
    def __init__(self, character_owner: 'Character', trait_type: TraitType = TraitType.SOCIAL):
        super().__init__(character_owner, trait_type)
        # display_name è già impostato da BaseTrait usando trait_type.display_name_it()
        # Puoi sovrascrivere self.description se necessario.
        self.description = "Questo NPC ama stare in compagnia, fare nuove amicizie e partecipare a eventi sociali." # Già presente

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