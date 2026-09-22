"""Derivazione del talent per una skill dal genoma.

Il talent è un moltiplicatore [0.5, 2.0] dell'apprendimento. Derivato
dalla sotto-famiglia di `TALENTS` corrispondente alla skill.

Il polygenic_score di una famiglia (38 loci × 2 alleli) ha media 0.5 e
deviazione standard ~0.033. Usiamo z-score amplificato per espandere il
range del talent in [0.5, 2.0].
"""

from __future__ import annotations

from typing import Final

from simai.npc.genetics.categories import GenomeCategory
from simai.npc.genetics.genome import Genome
from simai.npc.skills.enums import SKILL_TALENT_FAMILY, SkillType

#: Range del talent.
TALENT_MIN: Final[float] = 0.5
TALENT_MAX: Final[float] = 2.0

#: Deviazione standard teorica del polygenic_score per una famiglia di 38 loci.
#: Calcolo: `sqrt(1/12) / sqrt(38*2) ≈ 0.0331`.
_TALENT_STD: Final[float] = 0.033

#: Spread di amplificazione dello z-score.
#: z=±1 -> talent 1.25±0.40; z=±2 -> talent estremi (clampati).
_TALENT_SPREAD: Final[float] = 0.40

#: Talent centrale (z=0).
_TALENT_MID: Final[float] = 1.25

#: Mapping famiglia genetica -> categoria loci.
_FAMILY_TO_CATEGORY: Final[dict[str, GenomeCategory]] = {
    "PHYSICAL": GenomeCategory.TALENTS_PHYSICAL,
    "MENTAL": GenomeCategory.TALENTS_MENTAL,
    "SOCIAL": GenomeCategory.TALENTS_SOCIAL,
    "CREATIVE": GenomeCategory.TALENTS_CREATIVE,
}


def talent_for_skill(
    genome: Genome,
    skill_type: SkillType,
    *,
    mentorship_boost: float = 0.0,
) -> float:
    """Ritorna il talent per `skill_type` in [0.5, 2.0].

    `mentorship_boost` (default 0) viene aggiunto al valore base.
    """
    family_name = SKILL_TALENT_FAMILY.get(skill_type)
    if family_name is None:
        base = _TALENT_MID
    else:
        category = _FAMILY_TO_CATEGORY.get(family_name)
        if category is None:
            base = _TALENT_MID
        else:
            score = genome.polygenic_score(category)
            z = (score - 0.5) / _TALENT_STD
            base = _TALENT_MID + _TALENT_SPREAD * z
    return max(TALENT_MIN, min(TALENT_MAX, base + mentorship_boost))


def talent_map_for_genome(genome: Genome) -> dict[SkillType, float]:
    """Ritorna il talent per TUTTE le skill del genoma."""
    return {skill_type: talent_for_skill(genome, skill_type) for skill_type in SkillType}


__all__ = [
    "TALENT_MAX",
    "TALENT_MIN",
    "talent_for_skill",
    "talent_map_for_genome",
]
