"""ReputationService — opinioni e gossip."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.identity import IdentityService
from simai.npc.identity.enums import TabooReaction
from simai.npc.models import Character
from simai.npc.relationships.kinship import relationship_coefficient
from simai.npc.reputation.enums import (
    CONSANGUINITY_THRESHOLD,
    GossipTopic,
)
from simai.npc.reputation.models import GossipEvent, Opinion


@dataclass(frozen=True, slots=True)
class GossipResult:
    """Esito di un pettegolezzo."""

    propagated: bool
    topic: GossipTopic
    delta_opinion: float
    new_opinion: float


class ReputationService:
    """Servizio stateless per opinioni e gossip."""

    # ------------------------------------------------------------------
    # Opinion
    # ------------------------------------------------------------------

    @staticmethod
    def get_opinion(session: Session, observer_id: int, target_id: int) -> float:
        """Ritorna l'opinione di `observer_id` su `target_id` (default 0.0)."""
        row = session.scalars(
            select(Opinion).where(
                Opinion.observer_id == observer_id,
                Opinion.target_id == target_id,
            )
        ).first()
        return row.score if row is not None else 0.0

    @staticmethod
    def update_opinion(
        session: Session,
        *,
        observer_id: int,
        target_id: int,
        delta: float,
        current_dt: AnthalysDateTime,
    ) -> float:
        """Aggiorna l'opinione. Ritorna il nuovo score."""
        if observer_id == target_id:
            return 0.0

        row = session.scalars(
            select(Opinion).where(
                Opinion.observer_id == observer_id,
                Opinion.target_id == target_id,
            )
        ).first()

        now_secs = current_dt.to_total_seconds()
        if row is None:
            row = Opinion(
                observer_id=observer_id,
                target_id=target_id,
                score=0.0,
                last_updated_at_total_seconds=now_secs,
            )
            session.add(row)

        new_score = max(-100.0, min(100.0, row.score + delta))
        row.score = new_score
        row.last_updated_at_total_seconds = now_secs
        session.flush()
        return new_score

    @staticmethod
    def reputation_of(session: Session, target_id: int) -> float:
        """Reputazione pubblica = media delle opinioni su `target_id`."""
        result = session.scalar(
            select(func.avg(Opinion.score)).where(Opinion.target_id == target_id)
        )
        return float(result) if result is not None else 0.0

    @staticmethod
    def reputation_map(session: Session) -> dict[int, float]:
        """Mappa `{target_id: reputazione}` per tutti i character con opinioni."""
        rows = session.execute(
            select(Opinion.target_id, func.avg(Opinion.score)).group_by(Opinion.target_id)
        ).all()
        return {int(tid): float(avg) for tid, avg in rows}

    # ------------------------------------------------------------------
    # Gossip
    # ------------------------------------------------------------------

    @staticmethod
    def spread(
        session: Session,
        *,
        speaker: Character,
        listener: Character,
        target: Character,
        topic: GossipTopic,
        sentiment: float,
        current_dt: AnthalysDateTime,
        strength: float = 0.5,
        text: str | None = None,
    ) -> GossipResult:
        """Propaga un pettegolezzo da speaker a listener su target.

        Il listener aggiorna la propria opinione di target.
        """
        if sentiment < -1.0 or sentiment > 1.0:
            raise ValueError(f"sentiment in [-1, 1], ricevuto {sentiment}")
        if strength < 0.0 or strength > 1.0:
            raise ValueError(f"strength in [0, 1], ricevuto {strength}")

        if speaker.id == listener.id or target.id == listener.id:
            return GossipResult(False, topic, 0.0, 0.0)

        # Fattore 1: credibilità della fonte
        speaker_opinion = ReputationService.get_opinion(session, listener.id, speaker.id)
        source_credibility = 0.5 + 0.5 * max(-1.0, min(1.0, speaker_opinion / 100.0))

        # Fattore 2: confirmation bias (se già ha opinion negativa, ci crede di più)
        target_opinion_before = ReputationService.get_opinion(session, listener.id, target.id)
        confirmation = 1.0 - 0.3 * (target_opinion_before / 100.0)

        # Fattore 3: cultura del listener
        culture = IdentityService.get_culture(listener)
        culture_mod = 1.0
        if topic is GossipTopic.TABOO:
            if culture.reaction_to_taboo is TabooReaction.SEVERE:
                culture_mod = 1.5
            elif culture.reaction_to_taboo is TabooReaction.LENIENT:
                culture_mod = 0.5

        delta = sentiment * strength * 10.0 * source_credibility * confirmation * culture_mod

        new_score = ReputationService.update_opinion(
            session,
            observer_id=listener.id,
            target_id=target.id,
            delta=delta,
            current_dt=current_dt,
        )

        # Registro
        event = GossipEvent(
            source_id=speaker.id,
            target_id=target.id,
            listener_id=listener.id,
            topic=topic.value,
            sentiment=sentiment,
            strength=strength,
            text=text or f"Pettegolezzo {topic.value} su {target.full_name}",
            occurred_at_total_seconds=current_dt.to_total_seconds(),
            metadata_json={"delta": delta},
        )
        session.add(event)
        session.flush()

        logger.debug(
            "Gossip: {} -> {} su {} (topic={}, delta={:+.2f}, new={:+.2f})",
            speaker.id,
            listener.id,
            target.id,
            topic.value,
            delta,
            new_score,
        )

        return GossipResult(
            propagated=True,
            topic=topic,
            delta_opinion=delta,
            new_opinion=new_score,
        )

    @staticmethod
    def broadcast(
        session: Session,
        *,
        speaker: Character,
        witnesses: list[Character],
        target: Character,
        topic: GossipTopic,
        sentiment: float,
        current_dt: AnthalysDateTime,
        strength: float = 0.5,
    ) -> list[GossipResult]:
        """Propaga lo stesso pettegolezzo a più ascoltatori."""
        results: list[GossipResult] = []
        for listener in witnesses:
            r = ReputationService.spread(
                session,
                speaker=speaker,
                listener=listener,
                target=target,
                topic=topic,
                sentiment=sentiment,
                current_dt=current_dt,
                strength=strength,
            )
            results.append(r)
        return results

    # ------------------------------------------------------------------
    # Consanguineità
    # ------------------------------------------------------------------

    @staticmethod
    def is_consanguineous(
        session: Session,
        a_id: int,
        b_id: int,
        *,
        threshold: float = CONSANGUINITY_THRESHOLD,
    ) -> bool:
        """``True`` se a e b hanno un coefficiente di relazione >= threshold."""
        if a_id == b_id:
            return True
        r = relationship_coefficient(session, a_id, b_id)
        return r >= threshold

    @staticmethod
    def consanguinity_severity(
        session: Session,
        a: Character,
        b: Character,
    ) -> float:
        """Ritorna un fattore [0, 1] che rappresenta la "gravità" del taboo.

        - 0 = nessun taboo
        - 1 = taboo massimo (fratelli, genitori-figli, SEVERE culture)

        Combina `r` e la reazione al taboo del più severo dei due.
        """
        if a.id == b.id:
            return 1.0
        r = relationship_coefficient(session, a.id, b.id)
        if r < CONSANGUINITY_THRESHOLD:
            return 0.0

        # Base = r normalizzato su [0, 0.5] -> [0, 1]
        base = min(1.0, r / 0.5)

        # Modulazione cultura (prendi il più severo)
        cult_a = IdentityService.get_culture(a)
        cult_b = IdentityService.get_culture(b)
        culture_factor = 0.5
        for c in (cult_a, cult_b):
            if c.reaction_to_taboo is TabooReaction.SEVERE:
                culture_factor = max(culture_factor, 1.0)
            elif c.reaction_to_taboo is TabooReaction.LENIENT:
                culture_factor = min(culture_factor, 0.3)

        return min(1.0, base * culture_factor)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def witnesses_in_same_location(
        session: Session,
        actor: Character,
        *,
        exclude_ids: list[int] | None = None,
    ) -> list[Character]:
        """Character vivi nella stessa location dell'actor (escluso sé stesso)."""
        if actor.location_id is None:
            return []
        excluded = set(exclude_ids or []) | {actor.id}
        rows = session.scalars(
            select(Character).where(
                Character.location_id == actor.location_id,
                Character.is_alive.is_(True),
                Character.id.not_in(excluded),
            )
        ).all()
        return list(rows)


__all__ = ["GossipResult", "ReputationService"]
