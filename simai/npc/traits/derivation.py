"""Derivazione dei tratti e dell'aspirazione dal genoma."""

from __future__ import annotations

import random
from typing import Final

from simai.npc.genetics.categories import GenomeCategory
from simai.npc.genetics.genome import Genome
from simai.npc.traits.definitions import ASPIRATION_WEIGHTS, TRAIT_DEFS
from simai.npc.traits.enums import Aspiration, Trait, TraitFamily

#: Numero minimo di tratti attivi per personaggio.
MIN_TRAITS: Final[int] = 2

#: Numero massimo di tratti attivi per personaggio.
MAX_TRAITS: Final[int] = 6

#: Probabilità che un personaggio abbia una "maschera" (tratto di facciata).
MASK_PROBABILITY: Final[float] = 0.15


def _family_score(genome: Genome, family: TraitFamily) -> float:
    """Score poligenico della famiglia genetica `family`."""
    cat = GenomeCategory(family.value)
    return genome.polygenic_score(cat)


def derive_traits(genome: Genome, rng: random.Random) -> list[Trait]:
    """Deriva i tratti attivi dal genoma.

    Algoritmo:
      1. Per ogni tratto, calcola score della famiglia genetica.
      2. Attiva se score >= min_score.
      3. Se < MIN_TRAITS, integra con i tratti con score più alto (top-K).
      4. Se > MAX_TRAITS, tiene i primi MAX_TRAITS per margine (score - min_score).
      5. Ordina il risultato per nome (deterministico).

    `rng` è usato solo per tie-breaking se serve (non in questa versione).
    """
    del rng  # attualmente non usato, mantenuto per future logiche di tie-break

    family_scores: dict[TraitFamily, float] = {
        family: _family_score(genome, family) for family in TraitFamily
    }

    # Attivazione
    active: list[tuple[Trait, float]] = []  # (trait, margin)
    for trait, tdef in TRAIT_DEFS.items():
        family_score = family_scores[tdef.family]
        if family_score >= tdef.min_score:
            margin = family_score - tdef.min_score
            active.append((trait, margin))

    # Garanzia minima
    if len(active) < MIN_TRAITS:
        # Aggiungi i tratti con score di famiglia più alto non ancora attivi
        candidates: list[tuple[Trait, float]] = []
        for trait, tdef in TRAIT_DEFS.items():
            if any(t == trait for t, _ in active):
                continue
            family_score = family_scores[tdef.family]
            candidates.append((trait, family_score))
        candidates.sort(key=lambda x: -x[1])
        needed = MIN_TRAITS - len(active)
        active.extend(candidates[:needed])

    # Troncamento
    if len(active) > MAX_TRAITS:
        active.sort(key=lambda x: -x[1])
        active = active[:MAX_TRAITS]

    traits = sorted((t for t, _ in active), key=lambda t: t.value)
    return traits


def derive_mask_trait(base_traits: list[Trait], rng: random.Random) -> Trait | None:
    """Sceglie un tratto "maschera" non presente nei `base_traits`.

    Ritorna ``None`` se il personaggio non ha una maschera (probabilità
    `1 - MASK_PROBABILITY`) o se non ci sono tratti disponibili.
    """
    if rng.random() >= MASK_PROBABILITY:
        return None
    available = [t for t in Trait if t not in base_traits]
    if not available:
        return None
    return rng.choice(available)


def derive_aspiration(traits: list[Trait], genome: Genome, rng: random.Random) -> Aspiration:
    """Deriva l'aspirazione di vita dai tratti e dal genoma.

    Algoritmo: somma pesata dei tratti attivi per ciascuna aspirazione,
    + piccolo bonus dal genoma (dalla categoria TALENTS). `argmax` con
    tie-break casuale via `rng`.
    """
    scores: dict[Aspiration, float] = dict.fromkeys(Aspiration, 0.0)
    for trait in traits:
        for aspiration, weights in ASPIRATION_WEIGHTS.items():
            scores[aspiration] += weights.get(trait, 0.0)

    # Bonus genome-based: talenti alti favoriscono CAREER/CREATIVITY
    talent_score = genome.polygenic_score(GenomeCategory.TALENTS)
    scores[Aspiration.CAREER] += talent_score * 0.5
    scores[Aspiration.CREATIVITY] += talent_score * 0.5

    max_score = max(scores.values())
    top = [a for a, s in scores.items() if s == max_score]
    if len(top) == 1:
        return top[0]
    return rng.choice(top)


def traits_to_names(traits: list[Trait]) -> list[str]:
    """Converte una lista di `Trait` in lista di stringhe (per storage JSON)."""
    return [t.value for t in traits]


def names_to_traits(names: list[str]) -> list[Trait]:
    """Converte una lista di stringhe in `Trait`. Ignora valori sconosciuti."""
    result: list[Trait] = []
    for name in names:
        try:
            result.append(Trait(name))
        except ValueError:
            continue
    return result


__all__ = [
    "MASK_PROBABILITY",
    "MAX_TRAITS",
    "MIN_TRAITS",
    "derive_aspiration",
    "derive_mask_trait",
    "derive_traits",
    "names_to_traits",
    "traits_to_names",
]
