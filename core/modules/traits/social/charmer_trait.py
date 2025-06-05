# core/modules/traits/social/charmer_trait.py
from typing import TYPE_CHECKING, Optional, Dict, Any
from core.enums.trait_types import TraitType
from ..base_trait import BaseTrait

if TYPE_CHECKING:
    from core.character import Character

class CharmerTrait(BaseTrait):
    def __init__(self, character_owner: 'Character'):
        super().__init__(character_owner, TraitType.CHARMER)
        self.display_name = "Incantatore"
        self.description = "Questo NPC ha un modo affascinante di interagire e spesso ottiene ciò che vuole."

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