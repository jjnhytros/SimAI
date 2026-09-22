"""Layout dei loci genomici di Anthalys.

Il genoma è composto da **1024 loci diploidi** (2 alleli ciascuno) = 2048
valori totali. Ogni allele è un intero in [0, 255].

I loci sono organizzati in categorie contigue. La mappa `LOCI_LAYOUT`
definisce per ogni categoria l'intervallo `[start, end)` di loci.

Le categorie `TRAITS` e `TALENTS` sono suddivise in sotto-famiglie usate
dalla derivazione di tratti e talent. Il calcolo di `TOTAL_LOCI` esclude
le sotto-famiglie per evitare doppio conteggio.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class GenomeCategory(StrEnum):
    """Categorie di loci genomici."""

    APPEARANCE_HEIGHT = "APPEARANCE_HEIGHT"
    APPEARANCE_EYE_COLOR = "APPEARANCE_EYE_COLOR"
    APPEARANCE_HAIR_COLOR = "APPEARANCE_HAIR_COLOR"
    APPEARANCE_HAIR_TEXTURE = "APPEARANCE_HAIR_TEXTURE"
    APPEARANCE_SKIN_TONE = "APPEARANCE_SKIN_TONE"
    APPEARANCE_BUILD = "APPEARANCE_BUILD"
    APPEARANCE_FACIAL = "APPEARANCE_FACIAL"
    TRAITS = "TRAITS"
    TRAITS_SOCIAL = "TRAITS_SOCIAL"
    TRAITS_MENTAL = "TRAITS_MENTAL"
    TRAITS_PHYSICAL = "TRAITS_PHYSICAL"
    TRAITS_CREATIVE = "TRAITS_CREATIVE"
    TRAITS_PRACTICAL = "TRAITS_PRACTICAL"
    TALENTS = "TALENTS"
    TALENTS_PHYSICAL = "TALENTS_PHYSICAL"
    TALENTS_MENTAL = "TALENTS_MENTAL"
    TALENTS_SOCIAL = "TALENTS_SOCIAL"
    TALENTS_CREATIVE = "TALENTS_CREATIVE"
    HEALTH = "HEALTH"
    METABOLISM = "METABOLISM"


#: Layout dei loci per categoria: `{categoria: (start, end)}` con `end` escluso.
#:
#: - `TRAITS` (380-530): 150 loci, partizionati in 5 sotto-famiglie da 30.
#: - `TALENTS` (530-680): 150 loci, partizionati in 4 sotto-famiglie.
#:   - PHYSICAL: 530-568 (38 loci)
#:   - MENTAL:   568-606 (38 loci)
#:   - SOCIAL:   606-644 (38 loci)
#:   - CREATIVE: 644-680 (36 loci)
LOCI_LAYOUT: Final[dict[GenomeCategory, tuple[int, int]]] = {
    GenomeCategory.APPEARANCE_HEIGHT: (0, 50),
    GenomeCategory.APPEARANCE_EYE_COLOR: (50, 100),
    GenomeCategory.APPEARANCE_HAIR_COLOR: (100, 150),
    GenomeCategory.APPEARANCE_HAIR_TEXTURE: (150, 180),
    GenomeCategory.APPEARANCE_SKIN_TONE: (180, 230),
    GenomeCategory.APPEARANCE_BUILD: (230, 280),
    GenomeCategory.APPEARANCE_FACIAL: (280, 380),
    GenomeCategory.TRAITS: (380, 530),
    GenomeCategory.TRAITS_SOCIAL: (380, 410),
    GenomeCategory.TRAITS_MENTAL: (410, 440),
    GenomeCategory.TRAITS_PHYSICAL: (440, 470),
    GenomeCategory.TRAITS_CREATIVE: (470, 500),
    GenomeCategory.TRAITS_PRACTICAL: (500, 530),
    GenomeCategory.TALENTS: (530, 680),
    GenomeCategory.TALENTS_PHYSICAL: (530, 568),
    GenomeCategory.TALENTS_MENTAL: (568, 606),
    GenomeCategory.TALENTS_SOCIAL: (606, 644),
    GenomeCategory.TALENTS_CREATIVE: (644, 680),
    GenomeCategory.HEALTH: (680, 930),
    GenomeCategory.METABOLISM: (930, 1024),
}

#: Categorie che NON si sovrappongono (esclude le sotto-famiglie TRAITS_*/TALENTS_*).
_NON_OVERLAPPING_CATEGORIES: Final[frozenset[GenomeCategory]] = frozenset(
    cat
    for cat in GenomeCategory
    if not cat.name.startswith("TRAITS_") and not cat.name.startswith("TALENTS_")
)

#: Numero totale di loci (1024), escludendo le sotto-famiglie.
TOTAL_LOCI: Final[int] = sum(
    end - start for cat, (start, end) in LOCI_LAYOUT.items() if cat in _NON_OVERLAPPING_CATEGORIES
)

#: Numero totale di alleli (2048).
TOTAL_ALLELES: Final[int] = TOTAL_LOCI * 2

MAX_ALLELE_VALUE: Final[int] = 255
MIN_ALLELE_VALUE: Final[int] = 0


def loci_range(category: GenomeCategory) -> tuple[int, int]:
    """Ritorna `(start, end)` dei loci della categoria (end escluso)."""
    try:
        return LOCI_LAYOUT[category]
    except KeyError as exc:
        raise ValueError(f"Categoria sconosciuta: {category!r}") from exc


def category_of(locus_index: int) -> GenomeCategory:
    """Ritorna la categoria di un locus per indice.

    Le sotto-famiglie hanno priorità sulle categorie aggregate.
    """
    if not (0 <= locus_index < TOTAL_LOCI):
        raise ValueError(f"locus_index deve essere in [0, {TOTAL_LOCI}), ricevuto {locus_index}")
    # Prima le sotto-famiglie (più specifiche)
    sub_families: tuple[GenomeCategory, ...] = (
        GenomeCategory.TRAITS_SOCIAL,
        GenomeCategory.TRAITS_MENTAL,
        GenomeCategory.TRAITS_PHYSICAL,
        GenomeCategory.TRAITS_CREATIVE,
        GenomeCategory.TRAITS_PRACTICAL,
        GenomeCategory.TALENTS_PHYSICAL,
        GenomeCategory.TALENTS_MENTAL,
        GenomeCategory.TALENTS_SOCIAL,
        GenomeCategory.TALENTS_CREATIVE,
    )
    for cat in sub_families:
        start, end = LOCI_LAYOUT[cat]
        if start <= locus_index < end:
            return cat
    # Poi le categorie aggregate/normal
    for cat, (start, end) in LOCI_LAYOUT.items():
        if cat in (GenomeCategory.TRAITS, GenomeCategory.TALENTS):
            continue
        if start <= locus_index < end:
            return cat
    # Fallback: aggregato
    if 380 <= locus_index < 530:
        return GenomeCategory.TRAITS
    return GenomeCategory.TALENTS


# Validazione a import-time.
assert TOTAL_LOCI == 1024, f"TOTAL_LOCI deve essere 1024, trovato {TOTAL_LOCI}"
assert TOTAL_ALLELES == 2048, f"TOTAL_ALLELES deve essere 2048, trovato {TOTAL_ALLELES}"


__all__ = [
    "LOCI_LAYOUT",
    "MAX_ALLELE_VALUE",
    "MIN_ALLELE_VALUE",
    "TOTAL_ALLELES",
    "TOTAL_LOCI",
    "GenomeCategory",
    "category_of",
    "loci_range",
]
