"""SocializationService — creazione automatica di relazioni.

Gira nel daily work del `LifecycleManager`:
  - Per ogni coppia di NPC che si trovano nella stessa location,
    valuta se possono diventare amici/partner in base a:
      - opinion reciproca alta
      - compatibility
      - desire (per partner)
      - assenza di relazione già esistente
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.desire import DesireService
from simai.npc.models import Character
from simai.npc.relationships.compatibility import CompatibilityService
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship
from simai.npc.relationships.service import (
    RelationshipError,
    create_relationship,
    relationship_exists,
)
from simai.npc.reputation import ReputationService
from simai.npc.socialization.enums import (
    DAILY_EVAL_PROBABILITY,
    INITIAL_FRIEND_STRENGTH,
    INITIAL_PARTNER_STRENGTH,
    MAX_NEW_RELATIONS_PER_DAY,
    MIN_AGE_FOR_PARTNER,
    MIN_COMPATIBILITY_FOR_PARTNER,
    MIN_DESIRE_FOR_PARTNER,
    MIN_OPINION_BEST_FRIEND,
    MIN_OPINION_FRIEND,
    MIN_OPINION_PARTNER,
    PARTNER_PROBABILITY,
    UPGRADE_PROBABILITY,
)


@dataclass(frozen=True, slots=True)
class SocializationReport:
    """Esito di un daily tick di socializzazione."""

    friendships_created: int = 0
    upgrades_to_best: int = 0
    partners_created: int = 0
    pairs_evaluated: int = 0


class SocializationService:
    """Servizio stateless di socializzazione automatica."""

    @staticmethod
    def daily_tick(
        session: Session,
        characters: list[Character],
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
    ) -> SocializationReport:
        """Valuta le coppie e crea nuove relazioni.

        Solo coppie nella stessa location sono considerate.
        """
        report = SocializationReport()

        # Raggruppa per location
        by_loc: dict[int, list[Character]] = {}
        for c in characters:
            if c.location_id is None or not c.is_alive:
                continue
            by_loc.setdefault(c.location_id, []).append(c)

        # Cap globale di nuove relazioni al giorno
        created_budget = MAX_NEW_RELATIONS_PER_DAY

        for group in by_loc.values():
            if len(group) < 2:
                continue
            for i, a in enumerate(group):
                if created_budget <= 0:
                    break
                for b in group[i + 1 :]:
                    if created_budget <= 0:
                        break
                    report = SocializationService._evaluate_pair(
                        session,
                        a,
                        b,
                        current_dt=current_dt,
                        rng=rng,
                        report=report,
                        budget=created_budget,
                    )
                    created_budget = MAX_NEW_RELATIONS_PER_DAY - (
                        report.friendships_created
                        + report.partners_created
                        + report.upgrades_to_best
                    )

        return report

    # ------------------------------------------------------------------
    # Pair evaluation
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_pair(
        session: Session,
        a: Character,
        b: Character,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        report: SocializationReport,
        budget: int,
    ) -> SocializationReport:
        if a.id == b.id:
            return report

        op_a = ReputationService.get_opinion(session, a.id, b.id)
        op_b = ReputationService.get_opinion(session, b.id, a.id)
        min_opinion = min(op_a, op_b)

        has_rel = (
            relationship_exists(session, from_id=a.id, to_id=b.id, kind=RelationshipKind.FRIEND_OF)
            or relationship_exists(
                session,
                from_id=a.id,
                to_id=b.id,
                kind=RelationshipKind.BEST_FRIEND_OF,
            )
            or relationship_exists(
                session,
                from_id=a.id,
                to_id=b.id,
                kind=RelationshipKind.PARTNER_OF,
            )
        )

        # Tenta upgrade BEST_FRIEND
        if has_rel and min_opinion >= MIN_OPINION_BEST_FRIEND:
            if rng.random() < UPGRADE_PROBABILITY:
                report = SocializationService._upgrade_to_best(
                    session, a, b, current_dt=current_dt, report=report
                )
            return report

        # Nuova relazione
        if has_rel:
            return report
        if rng.random() >= DAILY_EVAL_PROBABILITY:
            return report

        # Soglia per amicizia
        if min_opinion < MIN_OPINION_FRIEND:
            return report

        # Partner?
        if (
            min_opinion >= MIN_OPINION_PARTNER
            and rng.random() < PARTNER_PROBABILITY
            and SocializationService._can_be_partner(session, a, b, current_dt=current_dt)
        ):
            report = SocializationService._create_partner(
                session, a, b, current_dt=current_dt, report=report
            )
            return report

        # Amicizia
        report = SocializationService._create_friend(
            session, a, b, current_dt=current_dt, report=report
        )
        return report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _age_years(character: Character, current_dt: AnthalysDateTime) -> int:
        age_secs = current_dt.to_total_seconds() - character.birth_total_seconds
        return int(age_secs // SECONDS_PER_YEAR)

    @staticmethod
    def _can_be_partner(
        session: Session,
        a: Character,
        b: Character,
        *,
        current_dt: AnthalysDateTime,
    ) -> bool:
        age_a = SocializationService._age_years(a, current_dt)
        age_b = SocializationService._age_years(b, current_dt)
        if age_a < MIN_AGE_FOR_PARTNER or age_b < MIN_AGE_FOR_PARTNER:
            return False

        # Compatibility
        compat = CompatibilityService.compute(a, b)
        if compat < MIN_COMPATIBILITY_FOR_PARTNER:
            return False

        # Desire
        d_a = DesireService.get_current(a)
        d_b = DesireService.get_current(b)
        if min(d_a, d_b) < MIN_DESIRE_FOR_PARTNER:
            return False

        # Polyamory check
        from simai.npc.relationships.polyamory import PolyamoryService

        has_partner_a = PolyamoryService.has_partner(session, a.id)
        has_partner_b = PolyamoryService.has_partner(session, b.id)
        if has_partner_a or has_partner_b:
            ok, _ = PolyamoryService.can_add_partner(session, actor=a, target=b)
            if not ok:
                return False
        return True

    @staticmethod
    def _create_friend(
        session: Session,
        a: Character,
        b: Character,
        *,
        current_dt: AnthalysDateTime,
        report: SocializationReport,
    ) -> SocializationReport:
        try:
            create_relationship(
                session,
                from_id=a.id,
                to_id=b.id,
                kind=RelationshipKind.FRIEND_OF,
                strength=INITIAL_FRIEND_STRENGTH,
                since_total_seconds=current_dt.to_total_seconds(),
            )
        except RelationshipError:
            return report
        logger.info("Socialization: friendship created {} <-> {}", a.id, b.id)
        return SocializationReport(
            friendships_created=report.friendships_created + 1,
            upgrades_to_best=report.upgrades_to_best,
            partners_created=report.partners_created,
            pairs_evaluated=report.pairs_evaluated + 1,
        )

    @staticmethod
    def _create_partner(
        session: Session,
        a: Character,
        b: Character,
        *,
        current_dt: AnthalysDateTime,
        report: SocializationReport,
    ) -> SocializationReport:
        try:
            rels = create_relationship(
                session,
                from_id=a.id,
                to_id=b.id,
                kind=RelationshipKind.PARTNER_OF,
                strength=INITIAL_PARTNER_STRENGTH,
                since_total_seconds=current_dt.to_total_seconds(),
            )
        except RelationshipError:
            return report
        # Marca poliamoroso se uno dei due ha già partner
        from simai.npc.relationships.polyamory import PolyamoryService

        if PolyamoryService.has_partner(session, a.id) or PolyamoryService.has_partner(
            session, b.id
        ):
            for r in rels:
                PolyamoryService.mark_polyamorous(r)
        logger.info("Socialization: partnership created {} <-> {}", a.id, b.id)
        return SocializationReport(
            friendships_created=report.friendships_created,
            upgrades_to_best=report.upgrades_to_best,
            partners_created=report.partners_created + 1,
            pairs_evaluated=report.pairs_evaluated + 1,
        )

    @staticmethod
    def _upgrade_to_best(
        session: Session,
        a: Character,
        b: Character,
        *,
        current_dt: AnthalysDateTime,
        report: SocializationReport,
    ) -> SocializationReport:
        # Rimuovi FRIEND_OF (entrambe le direzioni), crea BEST_FRIEND_OF
        for from_id, to_id in ((a.id, b.id), (b.id, a.id)):
            for kind in (
                RelationshipKind.FRIEND_OF,
                RelationshipKind.BEST_FRIEND_OF,
            ):
                row = session.scalars(
                    select(Relationship).where(
                        Relationship.from_id == from_id,
                        Relationship.to_id == to_id,
                        Relationship.kind == kind.value,
                    )
                ).first()
                if row is not None and kind is RelationshipKind.FRIEND_OF:
                    session.delete(row)
        try:
            create_relationship(
                session,
                from_id=a.id,
                to_id=b.id,
                kind=RelationshipKind.BEST_FRIEND_OF,
                strength=INITIAL_FRIEND_STRENGTH + 0.2,
                since_total_seconds=current_dt.to_total_seconds(),
            )
        except RelationshipError:
            return report
        logger.info("Socialization: best-friend upgrade {} <-> {}", a.id, b.id)
        return SocializationReport(
            friendships_created=report.friendships_created,
            upgrades_to_best=report.upgrades_to_best + 1,
            partners_created=report.partners_created,
            pairs_evaluated=report.pairs_evaluated + 1,
        )


__all__ = ["SocializationReport", "SocializationService"]
