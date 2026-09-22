"""Package `simai.npc.genetics` — genetica simulata di Anthalys.

Contenuto:
  - `Genome`             — 1024 loci × 2 alleli = 2048 valori
  - `GenomeCategory`     — 11 categorie con layout contiguo
  - `generate_random_genome` — per NPC senza genitori
  - `generate_from_parents`  — ereditarietà mendeliana + mutazione
  - `generate_twins`         — gemelli identici / fraterni
  - `phenotype_from_genome`  — DNA → aspetto osservabile
"""

from simai.npc.genetics.categories import (
    LOCI_LAYOUT,
    MAX_ALLELE_VALUE,
    MIN_ALLELE_VALUE,
    TOTAL_ALLELES,
    TOTAL_LOCI,
    GenomeCategory,
    category_of,
    loci_range,
)
from simai.npc.genetics.genome import GENOME_FORMAT_VERSION, Genome
from simai.npc.genetics.inheritance import (
    IDENTICAL_TWIN_PROBABILITY,
    TWIN_PROBABILITY,
    generate_from_parents,
    generate_random_genome,
    generate_twins,
    roll_twins,
)
from simai.npc.genetics.mutation import (
    MAX_MUTATION_OFFSET,
    MUTATION_RATE,
    mutate_allele,
)
from simai.npc.genetics.phenotype import (
    build,
    eye_color,
    facial_shape,
    hair_color,
    hair_texture,
    height_cm,
    phenotype_from_genome,
    skin_tone,
)

__all__ = [
    "GENOME_FORMAT_VERSION",
    "IDENTICAL_TWIN_PROBABILITY",
    "LOCI_LAYOUT",
    "MAX_ALLELE_VALUE",
    "MAX_MUTATION_OFFSET",
    "MIN_ALLELE_VALUE",
    "MUTATION_RATE",
    "TOTAL_ALLELES",
    "TOTAL_LOCI",
    "TWIN_PROBABILITY",
    "Genome",
    "GenomeCategory",
    "build",
    "category_of",
    "eye_color",
    "facial_shape",
    "generate_from_parents",
    "generate_random_genome",
    "generate_twins",
    "hair_color",
    "hair_texture",
    "height_cm",
    "loci_range",
    "mutate_allele",
    "phenotype_from_genome",
    "roll_twins",
    "skin_tone",
]
