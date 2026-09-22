"""Genome — rappresentazione immutabile del DNA di un Character.

Struttura: 1024 loci diploidi, ciascuno una coppia `(allele_a, allele_b)`
con valori interi in [0, 255]. Totale: 2048 alleli.

Serializzazione: `{"version": 1, "loci": [[a1, b1], [a2, b2], ...]}`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from simai.npc.genetics.categories import (
    MAX_ALLELE_VALUE,
    MIN_ALLELE_VALUE,
    TOTAL_LOCI,
    GenomeCategory,
    category_of,
    loci_range,
)

#: Versione del formato JSON. Incrementare in caso di breaking changes.
GENOME_FORMAT_VERSION: Final[int] = 1


@dataclass(frozen=True, slots=True)
class Genome:
    """Genoma immutabile di un Character.

    Uso:
        g = Genome.random(rng)
        pair = g.locus(0)               # (a, b)
        sub = g.category_slice(GenomeCategory.APPEARANCE_HEIGHT)
    """

    loci: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if len(self.loci) != TOTAL_LOCI:
            raise ValueError(f"Genome deve avere {TOTAL_LOCI} loci, ricevuti {len(self.loci)}")
        for i, (a, b) in enumerate(self.loci):
            if not (MIN_ALLELE_VALUE <= a <= MAX_ALLELE_VALUE):
                raise ValueError(f"Locus {i}: allele_a={a} fuori range [0, 255]")
            if not (MIN_ALLELE_VALUE <= b <= MAX_ALLELE_VALUE):
                raise ValueError(f"Locus {i}: allele_b={b} fuori range [0, 255]")

    # ------------------------------------------------------------------
    # Accesso
    # ------------------------------------------------------------------

    def locus(self, index: int) -> tuple[int, int]:
        """Coppia di alleli al locus `index`."""
        return self.loci[index]

    def category_slice(self, category: GenomeCategory) -> tuple[tuple[int, int], ...]:
        """Sottotuple dei loci appartenenti a `category`."""
        start, end = loci_range(category)
        return self.loci[start:end]

    def mean_allele(self, category: GenomeCategory) -> float:
        """Media di tutti gli alleli (entrambi) nella categoria, in [0, 255]."""
        start, end = loci_range(category)
        total = 0
        count = 0
        for i in range(start, end):
            a, b = self.loci[i]
            total += a + b
            count += 2
        return total / count if count else 0.0

    def polygenic_score(self, category: GenomeCategory) -> float:
        """Punteggio poligenico normalizzato in [0, 1] per una categoria.

        Definizione: media degli alleli nella categoria divisa per
        `MAX_ALLELE_VALUE`. Ordine 0 = tutti alleli a 0, ordine 1 = tutti a 255.
        """
        return self.mean_allele(category) / MAX_ALLELE_VALUE

    def allele_count(self) -> int:
        """Numero totale di alleli (2048)."""
        return len(self.loci) * 2

    # ------------------------------------------------------------------
    # Serializzazione
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serializza il genoma per storage JSON."""
        return {
            "version": GENOME_FORMAT_VERSION,
            "loci": [list(pair) for pair in self.loci],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Genome:
        """Deserializza un genoma da dict JSON. Solleva ValueError se malformato."""
        version = data.get("version")
        if version != GENOME_FORMAT_VERSION:
            raise ValueError(
                f"Versione genoma non supportata: {version} (attesa {GENOME_FORMAT_VERSION})"
            )
        raw_loci = data.get("loci")
        if not isinstance(raw_loci, list):
            raise ValueError("Genome: campo 'loci' mancante o non lista")
        if len(raw_loci) != TOTAL_LOCI:
            raise ValueError(f"Genome: attesi {TOTAL_LOCI} loci, ricevuti {len(raw_loci)}")
        pairs: list[tuple[int, int]] = []
        for i, pair in enumerate(raw_loci):
            if not (isinstance(pair, list) and len(pair) == 2):
                raise ValueError(f"Genome: locus {i} non è una coppia [a, b]")
            a, b = pair
            if not isinstance(a, int) or not isinstance(b, int):
                raise ValueError(f"Genome: locus {i} contiene valori non int")
            pairs.append((a, b))
        return cls(loci=tuple(pairs))

    @classmethod
    def empty(cls) -> Genome:
        """Genoma vuoto (tutti alleli a 0). Utile per test/dry-run."""
        return cls(loci=tuple((0, 0) for _ in range(TOTAL_LOCI)))

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, float]:
        """Riepilogo: punteggio poligenico per categoria."""
        return {str(cat): self.polygenic_score(cat) for cat in GenomeCategory}

    def category_of_locus(self, index: int) -> GenomeCategory:
        return category_of(index)


__all__ = ["GENOME_FORMAT_VERSION", "Genome"]
