"""BreakupService — rottura di relazioni."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.memory.enums import MemoryKind
from simai.npc.memory.service import MemoryService
from simai.npc.models import Character
from simai.npc.mood import Moodlet, MoodState
from simai.npc.relationships.boredom import STALE_THRESHOLD, BoredomService
from simai.npc.relationships.enums import RelationshipKind
from simai.npc.relationships.models import Relationship

#: Probabilità giornaliera di breakup data una relazione stale.
DAILY_BREAKUP_PROBABILITY: Final[float] = 0.01

#: Soglia di opinion sotto cui scatta breakup automatico.
OPINION_BREAKUP_THRESHOLD: Final[float] = -60.0

#: Moodlet durata e delta per breakup.
BREAKUP_MOODLET_DURATION: Final[int] = 500
BREAKUP_MOODLET_DELTA: Final[float] = -0.45


@dataclass(frozen=True, slots=True)
class BreakupResult:
    """Esito di un breakup."""

    occurred: bool
    kind: RelationshipKind | None
    reason: str
    residual_strength: float


class BreakupService:
    """Servizio stateless di rottura relazioni."""

    @staticmethod
    def should_break_up(
        session: Session,
        rel: Relationship,
        rng: random.Random,
    ) -> tuple[bool, str]:
        """Decide se una relazione deve rompersi ora."""
        # Skip: relazioni family (PARENT_OF/MENTOR_OF non si rompono)
        kind = RelationshipKind(rel.kind)
        if kind in (RelationshipKind.PARENT_OF, RelationshipKind.MENTOR_OF):
            return False, "family"

        boredom = BoredomService.get_boredom(rel)
        if boredom < STALE_THRESHOLD:
            return False, "not_stale"

        if rng.random() < DAILY_BREAKUP_PROBABILITY:
            return True, "stale"

        return False, "rng_missed"

    @staticmethod
    def breakup(
        session: Session,
        *,
        rel: Relationship,
        reason: str,
        current_dt: AnthalysDateTime,
    ) -> BreakupResult:
        """Esegue la rottura. Rimuove la relazione, aggiunge EX_PARTNER_OF."""
        kind = RelationshipKind(rel.kind)
        a = session.get(Character, rel.from_id)
        b = session.get(Character, rel.to_id)
        if a is None or b is None:
            return BreakupResult(False, kind, "character_missing", 0.0)

        # 1. Cattura strength residua
        residual = max(0.0, rel.strength * 0.5)

        # 2. Rimuovi la relazione forward + reverse
        BreakupService._remove_rel(session, rel.from_id, rel.to_id, kind)
        BreakupService._remove_rel(session, rel.to_id, rel.from_id, kind)

        # 3. Se era romantica, aggiungi EX_PARTNER_OF
        if kind in (RelationshipKind.PARTNER_OF, RelationshipKind.SPOUSE_OF):
            BreakupService._add_ex_partner(
                session,
                a_id=rel.from_id,
                b_id=rel.to_id,
                residual_strength=residual,
            )
            BreakupService._add_ex_partner(
                session,
                a_id=rel.to_id,
                b_id=rel.from_id,
                residual_strength=residual,
            )

        # 4. Moodlet negativo su entrambi
        BreakupService._apply_breakup_mood(a, kind, current_dt)
        BreakupService._apply_breakup_mood(b, kind, current_dt)

        # 5. Memoria EMOTIONAL
        for owner, other in ((a, b), (b, a)):
            MemoryService.record(
                session,
                owner_id=owner.id,
                kind=MemoryKind.EMOTIONAL,
                text=f"Rottura con {other.full_name} ({reason})",
                current_dt=current_dt,
                valence=-0.85,
                saliency=0.75,
                participants=[other.id],
                tags=["breakup", kind.value.lower()],
                lifecycle_event=True,
            )

        # 6. Opinion negativa reciproca
        from simai.npc.reputation import ReputationService

        ReputationService.update_opinion(
            session,
            observer_id=a.id,
            target_id=b.id,
            delta=-25.0,
            current_dt=current_dt,
        )
        ReputationService.update_opinion(
            session,
            observer_id=b.id,
            target_id=a.id,
            delta=-25.0,
            current_dt=current_dt,
        )

        session.flush()
        logger.info(
            "Breakup: {} ↔ {} (kind={}, reason={})",
            a.id,
            b.id,
            kind.value,
            reason,
        )
        return BreakupResult(True, kind, reason, residual)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _remove_rel(
        session: Session,
        from_id: int,
        to_id: int,
        kind: RelationshipKind,
    ) -> None:
        rows = list(
            session.scalars(
                select(Relationship).where(
                    Relationship.from_id == from_id,
                    Relationship.to_id == to_id,
                    Relationship.kind == kind.value,
                )
            )
        )
        for r in rows:
            session.delete(r)

    @staticmethod
    def _add_ex_partner(
        session: Session,
        *,
        a_id: int,
        b_id: int,
        residual_strength: float,
    ) -> None:
        """Crea una relazione EX_PARTNER_OF (se non esiste)."""
        existing = session.scalars(
            select(Relationship).where(
                Relationship.from_id == a_id,
                Relationship.to_id == b_id,
                Relationship.kind == RelationshipKind.EX_PARTNER_OF.value,
            )
        ).first()
        if existing is not None:
            existing.strength = residual_strength
            return
        session.add(
            Relationship(
                from_id=a_id,
                to_id=b_id,
                kind=RelationshipKind.EX_PARTNER_OF.value,
                strength=residual_strength,
                metadata_json={"since_breakup": True},
            )
        )

    @staticmethod
    def _apply_breakup_mood(
        character: Character,
        kind: RelationshipKind,
        current_dt: AnthalysDateTime,
    ) -> None:
        severity = (
            BREAKUP_MOODLET_DELTA
            if kind in (RelationshipKind.PARTNER_OF, RelationshipKind.SPOUSE_OF)
            else -0.25
        )
        mood = MoodState.from_dict(character.mood_json or {})
        moodlet = Moodlet(
            name=f"Rottura ({kind.value})",
            remaining_ticks=BREAKUP_MOODLET_DURATION,
            happiness_delta=severity,
            source="breakup",
        )
        from simai.npc.needs.needs import Needs

        new_mood = mood.tick(Needs.from_dict(character.needs_json or {}), (moodlet,))
        character.mood_json = new_mood.to_dict()


__all__ = [
    "BREAKUP_MOODLET_DELTA",
    "BREAKUP_MOODLET_DURATION",
    "DAILY_BREAKUP_PROBABILITY",
    "OPINION_BREAKUP_THRESHOLD",
    "BreakupResult",
    "BreakupService",
]
