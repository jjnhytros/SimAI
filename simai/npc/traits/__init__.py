"""Package `simai.npc.traits` — tratti, personalità, aspirazioni."""

from simai.npc.traits.definitions import ASPIRATION_WEIGHTS, TRAIT_DEFS, TraitDef
from simai.npc.traits.derivation import (
    MASK_PROBABILITY,
    MAX_TRAITS,
    MIN_TRAITS,
    derive_aspiration,
    derive_mask_trait,
    derive_traits,
    names_to_traits,
    traits_to_names,
)
from simai.npc.traits.enums import Aspiration, Trait, TraitCategory, TraitFamily

__all__ = [
    "ASPIRATION_WEIGHTS",
    "MASK_PROBABILITY",
    "MAX_TRAITS",
    "MIN_TRAITS",
    "TRAIT_DEFS",
    "Aspiration",
    "Trait",
    "TraitCategory",
    "TraitDef",
    "TraitFamily",
    "derive_aspiration",
    "derive_mask_trait",
    "derive_traits",
    "names_to_traits",
    "traits_to_names",
]
