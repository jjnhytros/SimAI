"""LibidoService — libido baseline + effective per relazione.

- baseline: [0, 1] per character, derivata da `sexuality.romantic_vs_sexual`
  e da `INTIMACY` need. Salvata in `attributes_json["libido"]`.
- effective: in una specifica relazione, `baseline × compatibility × connection`.
- asymmetry: |eff_a - eff_b| penalizza willingness.
"""

from __future__ import annotations

import random
from typing import Final

from simai.npc.identity import IdentityService
from simai.npc.models import Character
from simai.npc.relationships.compatibility import CompatibilityService
from simai.npc.relationships.connection import ConnectionService
from simai.npc.relationships.models import Relationship

#: Range libido.
MIN_LIBIDO: Final[float] = 0.10
MAX_LIBIDO: Final[float] = 0.95

#: Fattore di penalità per mismatch di libido.
MISMATCH_PENALTY: Final[float] = 0.40

#: Soglia oltre cui il mismatch è "significativo".
MISMATCH_THRESHOLD: Final[float] = 0.30


class LibidoService:
    """Servizio stateless di gestione della libido."""

    # ------------------------------------------------------------------
    # Baseline (per character)
    # ------------------------------------------------------------------

    @staticmethod
    def initialize_baseline(
        character: Character,
        rng: random.Random,
    ) -> float:
        """Libido iniziale da sexuality + rumore."""
        sexuality = IdentityService.get_sexuality(character)
        # Media di attrazioni + romantic_vs_sexual (che è più sessuale)
        attraction_avg = (
            sexuality.attraction_to_male
            + sexuality.attraction_to_female
            + sexuality.attraction_to_nonbinary
        ) / 3.0
        raw = 0.5 * attraction_avg + 0.5 * sexuality.romantic_vs_sexual
        value = MIN_LIBIDO + (MAX_LIBIDO - MIN_LIBIDO) * raw
        value += rng.uniform(-0.05, 0.05)
        return max(MIN_LIBIDO, min(MAX_LIBIDO, value))

    @staticmethod
    def get_baseline(character: Character) -> float:
        data = (character.attributes_json or {}).get("libido")
        if isinstance(data, dict):
            try:
                return max(MIN_LIBIDO, min(MAX_LIBIDO, float(data.get("baseline", 0.5))))
            except (TypeError, ValueError):
                return 0.5
        return 0.5

    @staticmethod
    def write_baseline(character: Character, value: float) -> None:
        attrs = dict(character.attributes_json or {})
        existing = attrs.get("libido")
        data = dict(existing) if isinstance(existing, dict) else {}
        data["baseline"] = max(MIN_LIBIDO, min(MAX_LIBIDO, value))
        attrs["libido"] = data
        character.attributes_json = attrs

    # ------------------------------------------------------------------
    # Effective (per relazione)
    # ------------------------------------------------------------------

    @staticmethod
    def effective(
        a: Character,
        b: Character,
        rel: Relationship,
    ) -> tuple[float, float]:
        """Ritorna `(libido_a, libido_b)` effective in questa relazione."""
        base_a = LibidoService.get_baseline(a)
        base_b = LibidoService.get_baseline(b)
        compat = CompatibilityService.compute(a, b)
        conn = ConnectionService.get(rel)
        multiplier = (0.5 + 0.5 * compat) * (0.7 + 0.3 * conn)
        return (
            max(0.0, min(1.0, base_a * multiplier)),
            max(0.0, min(1.0, base_b * multiplier)),
        )

    @staticmethod
    def asymmetry_factor(a: Character, b: Character, rel: Relationship) -> float:
        """Fattore di willingness basato su mismatch di libido.

        Ritorna un valore in [1 - MISMATCH_PENALTY, 1.0].
        """
        eff_a, eff_b = LibidoService.effective(a, b, rel)
        mismatch = abs(eff_a - eff_b)
        if mismatch < MISMATCH_THRESHOLD:
            return 1.0
        # Scala lineare da threshold a 1.0
        scaled = (mismatch - MISMATCH_THRESHOLD) / (1.0 - MISMATCH_THRESHOLD)
        penalty = min(MISMATCH_PENALTY, MISMATCH_PENALTY * scaled)
        return 1.0 - penalty

    @staticmethod
    def mismatch_label(a: Character, b: Character, rel: Relationship) -> str:
        eff_a, eff_b = LibidoService.effective(a, b, rel)
        diff = abs(eff_a - eff_b)
        if diff < 0.15:
            return "allineata"
        if diff < 0.30:
            return "lieve sbilanciamento"
        if diff < 0.50:
            return "sbilanciata"
        return "molto sbilanciata"


__all__ = [
    "MAX_LIBIDO",
    "MIN_LIBIDO",
    "MISMATCH_PENALTY",
    "MISMATCH_THRESHOLD",
    "LibidoService",
]
