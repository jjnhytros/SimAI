"""MemoryService — CRUD + decay + recall."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.memory.enums import DECAY_RATES, MIN_SALIENCY, MemoryKind
from simai.npc.memory.models import Memory
from simai.npc.memory.saliency import compute_saliency


@dataclass(frozen=True, slots=True)
class RecallResult:
    """Una memoria richiamata con il suo score di rilevanza."""

    memory: Memory
    score: float


class MemoryService:
    """Servizio stateless di gestione memorie."""

    # ------------------------------------------------------------------
    # Scrittura
    # ------------------------------------------------------------------

    @staticmethod
    def record(
        session: Session,
        *,
        owner_id: int,
        kind: MemoryKind,
        text: str,
        current_dt: AnthalysDateTime,
        valence: float = 0.0,
        saliency: float | None = None,
        participants: list[int] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        critical_needs: int = 0,
        strong_moodlets: int = 0,
        social_event: bool = False,
        lifecycle_event: bool = False,
    ) -> Memory:
        """Crea una memoria. Se `saliency` è None, la calcola dagli eventi."""
        if not text:
            raise ValueError("text non può essere vuoto")
        if not (-1.0 <= valence <= 1.0):
            raise ValueError(f"valence deve essere in [-1, 1], ricevuto {valence}")

        s = (
            saliency
            if saliency is not None
            else compute_saliency(
                critical_needs=critical_needs,
                strong_moodlets=strong_moodlets,
                social_event=social_event,
                lifecycle_event=lifecycle_event,
            )
        )
        if not (0.0 <= s <= 1.0):
            raise ValueError(f"saliency deve essere in [0, 1], ricevuto {s}")

        m = Memory(
            owner_id=owner_id,
            kind=kind.value,
            text=text,
            tick_total_seconds=current_dt.to_total_seconds(),
            saliency=s,
            valence=valence,
            participants_json=list(participants or []),
            tags_json=list(tags or []),
            metadata_json=dict(metadata or {}),
        )
        session.add(m)
        session.flush()
        return m

    # ------------------------------------------------------------------
    # Lettura
    # ------------------------------------------------------------------

    @staticmethod
    def recall(
        session: Session,
        owner_id: int,
        *,
        limit: int = 10,
        kind: MemoryKind | None = None,
        tag: str | None = None,
        participant_id: int | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> list[RecallResult]:
        """Ritorna le memorie del character, ordinate per rilevanza.

        Score = saliency × recency_factor
          - `recency_factor = 1 / (1 + days_since)`
        """
        if limit < 1:
            raise ValueError(f"limit deve essere >= 1, ricevuto {limit}")

        stmt = select(Memory).where(Memory.owner_id == owner_id)
        if kind is not None:
            stmt = stmt.where(Memory.kind == kind.value)

        rows = list(session.scalars(stmt))
        if tag is not None:
            rows = [m for m in rows if tag in (m.tags_json or [])]
        if participant_id is not None:
            rows = [m for m in rows if participant_id in (m.participants_json or [])]

        # Score
        cur_secs = current_dt.to_total_seconds() if current_dt is not None else None
        results: list[RecallResult] = []
        for m in rows:
            if cur_secs is None:
                recency = 1.0
            else:
                days_since = max(0, (cur_secs - m.tick_total_seconds) / SECONDS_PER_DAY)
                recency = 1.0 / (1.0 + days_since)
            results.append(RecallResult(memory=m, score=m.saliency * recency))

        results.sort(key=lambda r: -r.score)
        return results[:limit]

    @staticmethod
    def count(session: Session, owner_id: int) -> int:
        """Numero di memorie di un character."""
        rows = session.scalars(select(Memory).where(Memory.owner_id == owner_id))
        return len(list(rows))

    # ------------------------------------------------------------------
    # Decay
    # ------------------------------------------------------------------

    @staticmethod
    def decay(
        session: Session,
        *,
        elapsed_days: float,
    ) -> int:
        """Applica decay a tutte le memorie. Ritorna il numero eliminate.

        `elapsed_days` è il numero di giorni (frazionario) trascorsi.
        """
        if elapsed_days < 0:
            raise ValueError(f"elapsed_days deve essere >= 0, ricevuto {elapsed_days}")
        deleted = 0
        rows = list(session.scalars(select(Memory)))
        for m in rows:
            try:
                rate = DECAY_RATES[MemoryKind(m.kind)]
            except (ValueError, KeyError):
                rate = 0.01
            m.saliency = max(0.0, m.saliency - rate * elapsed_days)
            if m.saliency <= MIN_SALIENCY:
                session.delete(m)
                deleted += 1
        session.flush()
        return deleted


__all__ = ["MemoryService", "RecallResult"]
