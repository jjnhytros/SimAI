"""LGBTQService — disclosure, accettazione, dinamiche identitarie.

Il livello di disclosure è un float in [0, 1] in `attributes_json["lgbtq_disclosure"]`:
  - 0.0 = completamente nascosto
  - 1.0 = completamente pubblico

Il valore iniziale dipende dalla cultura di appartenenza.
"""

from __future__ import annotations

from typing import Final

from sqlalchemy.orm import Session

from simai.npc.identity.enums import TabooReaction
from simai.npc.identity.gender import (
    is_cisgender,
    is_heterosexual,
)
from simai.npc.identity.service import IdentityService
from simai.npc.models import Character

#: Disclosure di default per cultura.
DEFAULT_DISCLOSURE_SEVERE: Final[float] = 0.25
DEFAULT_DISCLOSURE_MODERATE: Final[float] = 0.60
DEFAULT_DISCLOSURE_LENIENT: Final[float] = 0.90

#: Soglia di disclosure per considerare "out" verso il pubblico.
PUBLIC_DISCLOSURE_THRESHOLD: Final[float] = 0.70


class LGBTQService:
    """Servizio stateless su identità non-cis / non-etero."""

    @staticmethod
    def is_lgbtq(character: Character) -> bool:
        """``True`` se il character è non-cis o non-etero."""
        # Non-cis
        if not is_cisgender(character.gender, character.sex):
            return True
        # Non-etero (via sexuality)
        sexuality = IdentityService.get_sexuality(character)
        return not is_heterosexual(character.sex, sexuality)

    @staticmethod
    def disclosure_level(character: Character) -> float:
        """Livello di disclosure in [0, 1]. Default da cultura se assente."""
        data = (character.attributes_json or {}).get("lgbtq_disclosure")
        if isinstance(data, (int, float)):
            return max(0.0, min(1.0, float(data)))
        return LGBTQService._default_disclosure_for(character)

    @staticmethod
    def set_disclosure(character: Character, value: float) -> None:
        """Imposta il livello di disclosure in `attributes_json`."""
        attrs = dict(character.attributes_json or {})
        attrs["lgbtq_disclosure"] = max(0.0, min(1.0, value))
        character.attributes_json = attrs

    @staticmethod
    def is_publicly_out(character: Character) -> bool:
        """``True`` se il character è "out" verso il pubblico."""
        if not LGBTQService.is_lgbtq(character):
            return False
        return LGBTQService.disclosure_level(character) >= PUBLIC_DISCLOSURE_THRESHOLD

    # ------------------------------------------------------------------
    # Accettazione (osservatore verso target)
    # ------------------------------------------------------------------

    @staticmethod
    def acceptance_factor(observer: Character, target: Character) -> float:
        """Fattore [0.2, 1.0]: quanto `observer` accetta l'identità di `target`.

        Ritorna 1.0 se `target` non è LGBTQ+.
        """
        if not LGBTQService.is_lgbtq(target):
            return 1.0
        # Se target non è out, observer non lo sa → nessuna penalità
        if not LGBTQService.is_publicly_out(target):
            return 1.0

        culture = IdentityService.get_culture(observer)
        if culture.reaction_to_taboo is TabooReaction.SEVERE:
            base = 0.40
        elif culture.reaction_to_taboo is TabooReaction.LENIENT:
            base = 1.00
        else:
            base = 0.75

        # Observer LGBTQ+ → empatia
        if LGBTQService.is_lgbtq(observer):
            base = min(1.0, base + 0.20)

        # Modestia riduce accettazione
        base -= culture.modesty * 0.15

        return max(0.20, min(1.0, base))

    @staticmethod
    def pair_acceptance_factor(session: Session, a: Character, b: Character) -> float:
        """Fattore combinato di accettazione reciproca."""
        return min(
            LGBTQService.acceptance_factor(a, b),
            LGBTQService.acceptance_factor(b, a),
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _default_disclosure_for(character: Character) -> float:
        culture = IdentityService.get_culture(character)
        if culture.reaction_to_taboo is TabooReaction.SEVERE:
            return DEFAULT_DISCLOSURE_SEVERE
        if culture.reaction_to_taboo is TabooReaction.LENIENT:
            return DEFAULT_DISCLOSURE_LENIENT
        return DEFAULT_DISCLOSURE_MODERATE


__all__ = [
    "DEFAULT_DISCLOSURE_LENIENT",
    "DEFAULT_DISCLOSURE_MODERATE",
    "DEFAULT_DISCLOSURE_SEVERE",
    "PUBLIC_DISCLOSURE_THRESHOLD",
    "LGBTQService",
]
