"""CompatibilityService — compatibilità intima tra due Character.

Combina 3 fattori in [0, 1]:
  - trait_overlap:  somiglianza dei tratti (Jaccard)
  - sexual_fit:     attrazione sessuale reciproca (cross-check)
  - cultural_fit:   distanza culturale (permissiveness, modesty)

Non è salvato: calcolato on-demand (economico). Se serve caching,
`Relationship.metadata_json["compatibility"]` può essere popolato
dal LifecycleManager in futuro.
"""

from __future__ import annotations

from typing import Final

from simai.npc.identity import IdentityService
from simai.npc.identity.models import Sexuality
from simai.npc.models import Character
from simai.npc.traits.derivation import names_to_traits

#: Pesi dei fattori (somma = 1.0).
W_TRAIT: Final[float] = 0.40
W_SEXUAL: Final[float] = 0.35
W_CULTURAL: Final[float] = 0.25

#: Offset di compatibilità dal trait_overlap (Jaccard 0..1 -> 0.3..1.0).
TRAIT_OVERLAP_FLOOR: Final[float] = 0.30


class CompatibilityService:
    """Servizio stateless di compatibilità."""

    @staticmethod
    def compute(a: Character, b: Character) -> float:
        """Ritorna la compatibilità in [0, 1]."""
        trait_score = CompatibilityService._trait_overlap(a, b)
        sexual_score = CompatibilityService._sexual_fit(a, b)
        cultural_score = CompatibilityService._cultural_fit(a, b)

        raw = W_TRAIT * trait_score + W_SEXUAL * sexual_score + W_CULTURAL * cultural_score
        return max(0.0, min(1.0, raw))

    # ------------------------------------------------------------------
    # Fattori
    # ------------------------------------------------------------------

    @staticmethod
    def _trait_overlap(a: Character, b: Character) -> float:
        """Jaccard similarity dei tratti, rimappato a [0.3, 1.0]."""
        traits_a = set(names_to_traits(a.traits_json or []))
        traits_b = set(names_to_traits(b.traits_json or []))
        if not traits_a and not traits_b:
            return 0.5
        union = traits_a | traits_b
        if not union:
            return 0.5
        jaccard = len(traits_a & traits_b) / len(union)
        return TRAIT_OVERLAP_FLOOR + (1.0 - TRAIT_OVERLAP_FLOOR) * jaccard

    @staticmethod
    def _sexual_fit(a: Character, b: Character) -> float:
        """Media della attrazione reciproca (0..1)."""
        sex_a = IdentityService.get_sexuality(a)
        sex_b = IdentityService.get_sexuality(b)

        def _attraction_to(sex_data: Sexuality, target_sex: str) -> float:
            if target_sex == "male":
                return sex_data.attraction_to_male
            if target_sex == "female":
                return sex_data.attraction_to_female
            return sex_data.attraction_to_nonbinary

        a_towards_b = _attraction_to(sex_a, b.sex)
        b_towards_a = _attraction_to(sex_b, a.sex)
        return (a_towards_b + b_towards_a) / 2.0

    @staticmethod
    def _cultural_fit(a: Character, b: Character) -> float:
        """Similarità culturale (1 - distanza media)."""
        ca = IdentityService.get_culture(a)
        cb = IdentityService.get_culture(b)
        diff_perm = abs(ca.permissiveness - cb.permissiveness)
        diff_mod = abs(ca.modesty - cb.modesty)
        diff_gen = abs(ca.gender_role_strict - cb.gender_role_strict)
        avg = (diff_perm + diff_mod + diff_gen) / 3.0
        return max(0.0, 1.0 - avg)

    # ------------------------------------------------------------------
    # Label (debug)
    # ------------------------------------------------------------------

    @staticmethod
    def label(score: float) -> str:
        if score >= 0.75:
            return "eccellente"
        if score >= 0.55:
            return "buona"
        if score >= 0.40:
            return "moderata"
        if score >= 0.25:
            return "debole"
        return "scarsa"


__all__ = [
    "TRAIT_OVERLAP_FLOOR",
    "W_CULTURAL",
    "W_SEXUAL",
    "W_TRAIT",
    "CompatibilityService",
]
