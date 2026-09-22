"""Generazione e trasmissione del genoma.

Funzioni:
  - `generate_random_genome(rng)` — genoma casuale (per NPC senza genitori)
  - `generate_from_parents(father, mother, rng)` — genoma ereditato
  - `generate_twins(father, mother, rng, identical)` — gemelli
"""

from __future__ import annotations

import random
from typing import Final

from simai.npc.genetics.categories import MAX_ALLELE_VALUE, TOTAL_LOCI
from simai.npc.genetics.genome import Genome
from simai.npc.genetics.mutation import mutate_allele

#: Probabilità (condizionale) che una gravidanza dia gemelli.
TWIN_PROBABILITY: Final[float] = 0.015

#: Probabilità che i gemelli siano identici (dato che sono gemelli).
IDENTICAL_TWIN_PROBABILITY: Final[float] = 0.30


def generate_random_genome(rng: random.Random) -> Genome:
    """Genera un genoma casuale. Ogni allele è uniforme in [0, 255]."""
    loci = tuple(
        (rng.randint(0, MAX_ALLELE_VALUE), rng.randint(0, MAX_ALLELE_VALUE))
        for _ in range(TOTAL_LOCI)
    )
    return Genome(loci=loci)


def generate_from_parents(
    father: Genome,
    mother: Genome,
    rng: random.Random,
) -> Genome:
    """Genera il genoma di un figlio da due genitori.

    Per ogni locus:
      - sceglie casualmente uno dei 2 alleli del padre
      - sceglie casualmente uno dei 2 alleli della madre
      - applica mutazione indipendentemente su ciascun allele
    """
    child_loci: list[tuple[int, int]] = []
    for i in range(TOTAL_LOCI):
        fa, fb = father.loci[i]
        ma, mb = mother.loci[i]
        allele_from_father = rng.choice((fa, fb))
        allele_from_mother = rng.choice((ma, mb))
        allele_from_father = mutate_allele(allele_from_father, rng)
        allele_from_mother = mutate_allele(allele_from_mother, rng)
        child_loci.append((allele_from_father, allele_from_mother))
    return Genome(loci=tuple(child_loci))


def generate_twins(
    father: Genome,
    mother: Genome,
    rng: random.Random,
    *,
    identical: bool,
) -> tuple[Genome, Genome]:
    """Genera una coppia di gemelli.

    - Identici (monozigoti): stessa copia del genoma.
    - Fraterni (dizigoti): due generazioni indipendenti dai genitori.
    """
    first = generate_from_parents(father, mother, rng)
    if identical:
        return (first, first)
    second = generate_from_parents(father, mother, rng)
    return (first, second)


def roll_twins(rng: random.Random) -> tuple[bool, bool]:
    """Determina se una gravidanza è gemellare e se i gemelli sono identici.

    Ritorna `(is_twin, identical)`.
    """
    is_twin = rng.random() < TWIN_PROBABILITY
    if not is_twin:
        return (False, False)
    identical = rng.random() < IDENTICAL_TWIN_PROBABILITY
    return (True, identical)


__all__ = [
    "IDENTICAL_TWIN_PROBABILITY",
    "TWIN_PROBABILITY",
    "generate_from_parents",
    "generate_random_genome",
    "generate_twins",
    "roll_twins",
]
