"""Mutazione degli alleli durante l'ereditarietà."""

from __future__ import annotations

import random
from typing import Final

from simai.npc.genetics.categories import MAX_ALLELE_VALUE, MIN_ALLELE_VALUE

#: Probabilità di mutazione per locus ad ogni trasmissione.
MUTATION_RATE: Final[float] = 0.01

#: Offset massimo di una mutazione (in valore allele, 0-255).
MAX_MUTATION_OFFSET: Final[int] = 20


def mutate_allele(allele: int, rng: random.Random) -> int:
    """Applica mutazione a un allele con probabilità `MUTATION_RATE`.

    Se muta, l'offset è uniforme in [-MAX, +MAX] (escluso 0).
    Il risultato è clampato in [0, 255].
    """
    if allele < MIN_ALLELE_VALUE or allele > MAX_ALLELE_VALUE:
        raise ValueError(f"allele fuori range [0, 255]: {allele}")
    if rng.random() >= MUTATION_RATE:
        return allele
    # Offset: scegli tra -MAX..-1 e +1..+MAX
    magnitude = rng.randint(1, MAX_MUTATION_OFFSET)
    sign = rng.choice([-1, 1])
    mutated = allele + sign * magnitude
    return max(MIN_ALLELE_VALUE, min(MAX_ALLELE_VALUE, mutated))


__all__ = ["MAX_MUTATION_OFFSET", "MUTATION_RATE", "mutate_allele"]
