"""Espressione fenotipica del genoma: dal DNA all'aspetto osservabile.

Per ogni categoria di aspetto, il punteggio poligenico (`polygenic_score`)
viene mappato a un valore osservabile:

  - Continuo (altezza): `min + score * (max - min)`
  - Discreto (occhi, capelli): binning del punteggio in fasce etichettate

Il sesso biologico modula i range dell'altezza e del build.
"""

from __future__ import annotations

from typing import Any

from simai.npc.enums import Sex
from simai.npc.genetics.categories import GenomeCategory
from simai.npc.genetics.genome import Genome


def _bin(value: float, bins: tuple[tuple[float, str], ...]) -> str:
    """Mappa `value` in [0, 1] a una stringa secondo bins `(soglia_sup, label)`."""
    for threshold, label in bins:
        if value < threshold:
            return label
    return bins[-1][1]


# ---------------------------------------------------------------------------
# Bins (soglie superiori)
# ---------------------------------------------------------------------------

_EYE_COLOR_BINS: tuple[tuple[float, str], ...] = (
    (0.15, "marrone scuro"),
    (0.35, "marrone"),
    (0.50, "nocciola"),
    (0.62, "verde"),
    (0.78, "ambra"),
    (0.92, "azzurro"),
    (1.01, "grigio"),
)

_HAIR_COLOR_BINS: tuple[tuple[float, str], ...] = (
    (0.12, "nero"),
    (0.35, "castano scuro"),
    (0.55, "castano"),
    (0.72, "biondo"),
    (0.88, "rosso"),
    (1.01, "bianco"),
)

_HAIR_TEXTURE_BINS: tuple[tuple[float, str], ...] = (
    (0.30, "liscio"),
    (0.55, "mosso"),
    (0.80, "riccio"),
    (1.01, "coily"),
)

_SKIN_TONE_BINS: tuple[tuple[float, str], ...] = (
    (0.15, "chiaro"),
    (0.30, "medio-chiaro"),
    (0.50, "medio"),
    (0.70, "medio-scuro"),
    (0.88, "scuro"),
    (1.01, "olivastro"),
)

_BUILD_BINS: tuple[tuple[float, str], ...] = (
    (0.20, "esile"),
    (0.40, "snello"),
    (0.60, "atletico"),
    (0.78, "robusto"),
    (0.92, "formoso"),
    (1.01, "massiccio"),
)

_FACIAL_SHAPE_BINS: tuple[tuple[float, str], ...] = (
    (0.25, "ovale"),
    (0.50, "tondo"),
    (0.75, "quadrato"),
    (1.01, "allungato"),
)


# ---------------------------------------------------------------------------
# Range altezza per sesso
# ---------------------------------------------------------------------------

_HEIGHT_RANGES_CM: dict[Sex, tuple[int, int]] = {
    Sex.MALE: (160, 200),
    Sex.FEMALE: (150, 185),
    Sex.INTERSEX: (155, 195),
}


# ---------------------------------------------------------------------------
# Espressione
# ---------------------------------------------------------------------------


def height_cm(genome: Genome, sex: Sex) -> int:
    """Altezza in cm in base al punteggio poligenico e al sesso."""
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_HEIGHT)
    lo, hi = _HEIGHT_RANGES_CM[sex]
    return int(lo + score * (hi - lo))


def eye_color(genome: Genome) -> str:
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_EYE_COLOR)
    return _bin(score, _EYE_COLOR_BINS)


def hair_color(genome: Genome) -> str:
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_HAIR_COLOR)
    return _bin(score, _HAIR_COLOR_BINS)


def hair_texture(genome: Genome) -> str:
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_HAIR_TEXTURE)
    return _bin(score, _HAIR_TEXTURE_BINS)


def skin_tone(genome: Genome) -> str:
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_SKIN_TONE)
    return _bin(score, _SKIN_TONE_BINS)


def build(genome: Genome) -> str:
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_BUILD)
    return _bin(score, _BUILD_BINS)


def facial_shape(genome: Genome) -> str:
    score = genome.polygenic_score(GenomeCategory.APPEARANCE_FACIAL)
    return _bin(score, _FACIAL_SHAPE_BINS)


def phenotype_from_genome(genome: Genome, sex: Sex) -> dict[str, Any]:
    """Dizionario completo dell'aspetto derivato dal genoma."""
    return {
        "height_cm": height_cm(genome, sex),
        "eye_color": eye_color(genome),
        "hair_color": hair_color(genome),
        "hair_texture": hair_texture(genome),
        "skin_tone": skin_tone(genome),
        "build": build(genome),
        "facial_shape": facial_shape(genome),
        "polygenic_scores": {
            "height": genome.polygenic_score(GenomeCategory.APPEARANCE_HEIGHT),
            "eye_color": genome.polygenic_score(GenomeCategory.APPEARANCE_EYE_COLOR),
            "hair_color": genome.polygenic_score(GenomeCategory.APPEARANCE_HAIR_COLOR),
            "hair_texture": genome.polygenic_score(GenomeCategory.APPEARANCE_HAIR_TEXTURE),
            "skin_tone": genome.polygenic_score(GenomeCategory.APPEARANCE_SKIN_TONE),
            "build": genome.polygenic_score(GenomeCategory.APPEARANCE_BUILD),
            "facial_shape": genome.polygenic_score(GenomeCategory.APPEARANCE_FACIAL),
        },
    }


__all__ = [
    "build",
    "eye_color",
    "facial_shape",
    "hair_color",
    "hair_texture",
    "height_cm",
    "phenotype_from_genome",
    "skin_tone",
]
