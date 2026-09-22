"""InfidelityService — infedeltà con discovery."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.models import Character
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship

#: Soglia opinion verso il terzo per considerare l'atto.
INFIDELITY_OPINION_THRESHOLD: Final[float] = 40.0

#: Soglia desire per considerare l'atto.
INFIDELITY_DESIRE_THRESHOLD: Final[float] = 0.70

#: Probabilità discovery se partner in stessa location.
DISCOVERY_IN_LOCATION: Final[float] = 0.70

#: Probabilità discovery per witness.
DISCOVERY_PER_WITNESS: Final[float] = 0.30

#: Probabilità discovery "rumor" per giorno se nessuno presente.
DISCOVERY_RUMOR_DAILY: Final[float] = 0.05

#: Delta opinion quando scoperto.
DISCOVERY_OPINION_DELTA_PARTNER: Final[float] = -50.0
DISCOVERY_OPINION_DELTA_TARGET: Final[float] = -30.0


@dataclass(frozen=True, slots=True)
class InfidelityAttempt:
    """Esito di un tentativo di infedeltà."""

    considered: bool
    reason: str
    partner_id: int | None
    target_id: int | None


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    """Esito di una scoperta."""

    discovered: bool
    by_partner: bool
    via_witness: bool
    via_rumor: bool
    broken_up: bool


class InfidelityService:
    """Servizio stateless di infedeltà."""

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------

    @staticmethod
    def primary_partner(session: Session, character_id: int) -> Character | None:
        """Ritorna il partner romantico principale (se esiste)."""
        rel = session.scalars(
            select(Relationship).where(
                Relationship.from_id == character_id,
                Relationship.kind.in_(
                    [
                        RelationshipKind.PARTNER_OF.value,
                        RelationshipKind.SPOUSE_OF.value,
                    ]
                ),
            )
        ).first()
        if rel is None:
            return None
        return session.get(Character, rel.to_id)

    @staticmethod
    def should_consider(
        session: Session,
        character: Character,
        target: Character,
        rng: random.Random,
    ) -> InfidelityAttempt:
        """Valuta se il character considererebbe un'infedeltà con target."""
        # Deve avere un partner romantico
        partner = InfidelityService.primary_partner(session, character.id)
        if partner is None:
            return InfidelityAttempt(False, "no_partner", None, target.id)
        if partner.id == target.id:
            return InfidelityAttempt(False, "partner_is_target", partner.id, target.id)

        # Opinion alta verso target
        from simai.npc.reputation import ReputationService

        opinion = ReputationService.get_opinion(session, character.id, target.id)
        if opinion < INFIDELITY_OPINION_THRESHOLD:
            return InfidelityAttempt(
                False, f"opinion_too_low ({opinion:.1f})", partner.id, target.id
            )

        # Desire alto
        from simai.npc.desire import DesireService

        desire = DesireService.get_current(character)
        if desire < INFIDELITY_DESIRE_THRESHOLD:
            return InfidelityAttempt(False, f"desire_too_low ({desire:.2f})", partner.id, target.id)

        # Boredom su relazione primaria
        rel_partner = session.scalars(
            select(Relationship).where(
                Relationship.from_id == character.id,
                Relationship.to_id == partner.id,
                Relationship.kind.in_(
                    [
                        RelationshipKind.PARTNER_OF.value,
                        RelationshipKind.SPOUSE_OF.value,
                    ]
                ),
            )
        ).first()
        if rel_partner is None:
            return InfidelityAttempt(False, "no_primary_rel", partner.id, target.id)

        from simai.npc.relationships.boredom import BoredomService

        boredom = BoredomService.get_boredom(rel_partner)
        if boredom < 0.40:
            return InfidelityAttempt(False, f"not_bored ({boredom:.2f})", partner.id, target.id)

        # RNG tiro
        if rng.random() > 0.15:
            return InfidelityAttempt(False, "rng_missed", partner.id, target.id)

        return InfidelityAttempt(True, "ok", partner.id, target.id)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_discovery(
        session: Session,
        *,
        actor: Character,
        target: Character,
        partner: Character,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> DiscoveryResult:
        """Determina se l'infedeltà viene scoperta.

        Fattori:
          - Partner in stessa location → 70% scoperta
          - Witness in stessa location → 30% ciascuno (accumulativo)
          - Nessuno → 5% "rumor"
        """
        discovered = False
        by_partner = False
        via_witness = False
        via_rumor = False

        # 1. Partner in stessa location?
        if (
            partner.location_id is not None
            and partner.location_id == actor.location_id
            and rng.random() < DISCOVERY_IN_LOCATION
        ):
            discovered = True
            by_partner = True

        # 2. Witness
        if not discovered:
            from simai.npc.reputation import ReputationService

            witnesses = ReputationService.witnesses_in_same_location(
                session, actor, exclude_ids=[target.id, partner.id]
            )
            for _ in witnesses:
                if rng.random() < DISCOVERY_PER_WITNESS:
                    discovered = True
                    via_witness = True
                    break

        # 3. Rumor
        if not discovered and rng.random() < DISCOVERY_RUMOR_DAILY:
            discovered = True
            via_rumor = True

        # Applica effetti se scoperto
        broken_up = False
        if discovered:
            broken_up = InfidelityService._apply_discovery_effects(
                session,
                actor=actor,
                target=target,
                partner=partner,
                current_dt=current_dt,
                by_partner=by_partner,
            )

        return DiscoveryResult(
            discovered=discovered,
            by_partner=by_partner,
            via_witness=via_witness,
            via_rumor=via_rumor,
            broken_up=broken_up,
        )

    @staticmethod
    def _apply_discovery_effects(
        session: Session,
        *,
        actor: Character,
        target: Character,
        partner: Character,
        current_dt: AnthalysDateTime,
        by_partner: bool,
    ) -> bool:
        """Applica opinion updates + breakup + gossip. Ritorna se breakup."""
        from simai.npc.reputation import GossipTopic, ReputationService

        # 1. Opinion del partner verso actor
        ReputationService.update_opinion(
            session,
            observer_id=partner.id,
            target_id=actor.id,
            delta=DISCOVERY_OPINION_DELTA_PARTNER,
            current_dt=current_dt,
        )
        # 2. Opinion di actor verso target (rabbia per essere stato scoperto)
        ReputationService.update_opinion(
            session,
            observer_id=actor.id,
            target_id=target.id,
            delta=DISCOVERY_OPINION_DELTA_TARGET,
            current_dt=current_dt,
        )

        # 3. Gossip scandalo (se c'è un witness)
        if not by_partner:
            ReputationService.spread(
                session,
                speaker=partner,
                listener=actor,
                target=actor,
                topic=GossipTopic.SCANDAL,
                sentiment=-0.9,
                strength=0.8,
                current_dt=current_dt,
            )

        # 4. Breakup forzato se partner è SPOUSE_OF / PARTNER_OF
        broken_up = False
        rel = session.scalars(
            select(Relationship).where(
                Relationship.from_id == partner.id,
                Relationship.to_id == actor.id,
                Relationship.kind.in_(
                    [
                        RelationshipKind.PARTNER_OF.value,
                        RelationshipKind.SPOUSE_OF.value,
                    ]
                ),
            )
        ).first()
        if rel is not None and by_partner:
            from simai.npc.relationships.breakup import BreakupService

            BreakupService.breakup(
                session,
                rel=rel,
                reason="infidelity",
                current_dt=current_dt,
            )
            broken_up = True

        logger.info(
            "Infidelity discovered: actor={} target={} partner={} by_partner={}",
            actor.id,
            target.id,
            partner.id,
            by_partner,
        )
        return broken_up


__all__ = [
    "DISCOVERY_IN_LOCATION",
    "DISCOVERY_OPINION_DELTA_PARTNER",
    "DISCOVERY_OPINION_DELTA_TARGET",
    "DISCOVERY_PER_WITNESS",
    "DISCOVERY_RUMOR_DAILY",
    "INFIDELITY_DESIRE_THRESHOLD",
    "INFIDELITY_OPINION_THRESHOLD",
    "DiscoveryResult",
    "InfidelityAttempt",
    "InfidelityService",
]
