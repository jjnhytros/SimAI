# core/modules/traits/social/charmer_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.social_interaction_types import SocialInteractionType
from core.enums.trait_types import TraitType
from core.modules.actions.social_actions import SocializeAction
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class CharmerTrait(BaseTrait):
    def __init__(self, character_owner: 'Character', trait_type: TraitType):
        trait_type = TraitType.CHARMER
        super().__init__(character_owner=character_owner, trait_type=trait_type)
        self.display_name = self.trait_type.display_name_it(character_owner.gender)
        self.description = "Ha un fascino naturale e ha successo nelle interazioni romantiche."

    def get_action_choice_priority_modifier(self, action, simulation_context):
        if isinstance(action, SocializeAction) and action.interaction_type == SocialInteractionType.FLIRT:
            return 2.0
        return 1.0

    def get_on_add_effects(self) -> Optional[Dict[str, Any]]:
        # Esempio: Aumenta leggermente la skill Carisma iniziale
        return None # Da definire

    def get_on_remove_effects(self) -> Optional[Dict[str, Any]]:
        return None

    # def get_relationship_modifier(self, target_npc: 'Character', relationship_type: 'RelationshipType') -> int:
    #     # Leggero bonus iniziale nelle relazioni sociali
    #     if relationship_type not in [RelationshipType.ENEMY_RIVAL, RelationshipType.ENEMY_DISLIKED]: # Nomi Enum da verificare
    #         return 5 
    #     return 0