"""TeenDynamicsService — dinamiche di coppia adolescenti.

Fattori:
  - willingness ridotta per azioni romantiche tra teen
  - opposizione parentale
  - segretezza della relazione
"""

from __future__ import annotations

from typing import Final

from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.models import Character
from simai.npc.relationships.family_tree import FamilyTreeService
from simai.npc.relationships.models import Relationship

#: Soglia per essere considerato "teen" (anni Anthalys).
TEEN_MIN_AGE: Final[int] = 13
TEEN_MAX_AGE: Final[int] = 18

#: Moltiplicatore di willingness per teen (azioni level ≥ 3).
TEEN_WILLINGNESS_MULT: Final[float] = 0.60

#: Moltiplicatore extra se entrambi teen e non sposati.
TEEN_BOTH_MULT: Final[float] = 0.85

#: Soglia opinion dei genitori sotto cui c'è opposizione.
PARENTAL_OPPOSITION_THRESHOLD: Final[float] = -20.0

#: Penalità di willingness per opposizione parentale.
PARENTAL_OPPOSITION_PENALTY: Final[float] = 0.30

#: Soglia età per "consenso informato" alle relazioni segrete.
MIN_SECRECY_AGE: Final[int] = 15


class TeenDynamicsService:
    """Servizio stateless di dinamiche adolescenziali."""

    @staticmethod
    def age_years(character: Character, current_dt: AnthalysDateTime) -> int:
        age_secs = current_dt.to_total_seconds() - character.birth_total_seconds
        return int(age_secs // SECONDS_PER_YEAR)

    @staticmethod
    def is_teen(character: Character, current_dt: AnthalysDateTime) -> bool:
        age = TeenDynamicsService.age_years(character, current_dt)
        return TEEN_MIN_AGE <= age < TEEN_MAX_AGE

    # ------------------------------------------------------------------
    # Willingness modifiers
    # ------------------------------------------------------------------

    @staticmethod
    def willingness_modifier(
        initiator: Character,
        partner: Character,
        *,
        current_dt: AnthalysDateTime,
        action_level: int,
    ) -> float:
        """Fattore [0.5, 1.0] per teen + azioni romantiche."""
        if action_level < 3:
            return 1.0
        a_teen = TeenDynamicsService.is_teen(initiator, current_dt)
        b_teen = TeenDynamicsService.is_teen(partner, current_dt)
        if not a_teen and not b_teen:
            return 1.0
        if a_teen and b_teen:
            return TEEN_WILLINGNESS_MULT * TEEN_BOTH_MULT
        return TEEN_WILLINGNESS_MULT

    # ------------------------------------------------------------------
    # Parental opposition
    # ------------------------------------------------------------------

    @staticmethod
    def parental_opposition_factor(
        session: Session,
        teen: Character,
        partner: Character,
        *,
        current_dt: AnthalysDateTime,
    ) -> tuple[float, list[int]]:
        """Ritorna `(factor, opposing_parent_ids)`.

        Factor ∈ [1 - PENALTY, 1.0].
        """
        from simai.npc.reputation import ReputationService

        parents = FamilyTreeService.parents_of(session, teen.id)
        if not parents:
            return 1.0, []

        opposing: list[int] = []
        for parent in parents:
            if not parent.is_alive:
                continue
            opinion = ReputationService.get_opinion(session, parent.id, partner.id)
            if opinion < PARENTAL_OPPOSITION_THRESHOLD:
                opposing.append(parent.id)

        if not opposing:
            return 1.0, []
        # Penalità proporzionale al numero di genitori contrari
        n_parents = max(1, len([p for p in parents if p.is_alive]))
        ratio = len(opposing) / n_parents
        factor = 1.0 - PARENTAL_OPPOSITION_PENALTY * ratio
        return max(0.5, factor), opposing

    # ------------------------------------------------------------------
    # Secrecy
    # ------------------------------------------------------------------

    @staticmethod
    def should_be_secret(
        teen: Character,
        *,
        current_dt: AnthalysDateTime,
        opposing_parent_ids: list[int],
    ) -> bool:
        """``True`` se la relazione dovrebbe essere tenuta segreta."""
        if not opposing_parent_ids:
            return False
        age = TeenDynamicsService.age_years(teen, current_dt)
        if age < MIN_SECRECY_AGE:
            return True
        # Teen più grandi possono decidere di essere aperti
        return len(opposing_parent_ids) > 1

    @staticmethod
    def mark_secret(rel: Relationship) -> None:
        md = dict(rel.metadata_json or {})
        md["secret"] = True
        rel.metadata_json = md

    @staticmethod
    def is_secret(rel: Relationship) -> bool:
        md = rel.metadata_json or {}
        return bool(md.get("secret", False))


__all__ = [
    "MIN_SECRECY_AGE",
    "PARENTAL_OPPOSITION_PENALTY",
    "PARENTAL_OPPOSITION_THRESHOLD",
    "TEEN_BOTH_MULT",
    "TEEN_MAX_AGE",
    "TEEN_MIN_AGE",
    "TEEN_WILLINGNESS_MULT",
    "TeenDynamicsService",
]
