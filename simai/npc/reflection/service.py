"""ReflectionService — genera e persiste riflessioni."""

from __future__ import annotations

import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.memory.enums import MemoryKind
from simai.npc.memory.service import MemoryService
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.reflection.enums import ReflectionKind
from simai.npc.reflection.models import ReflectionEntry
from simai.npc.reflection.templates import compose_reflection
from simai.npc.stress.service import StressService


@dataclass(frozen=True, slots=True)
class ReflectionResult:
    """Esito di una riflessione."""

    entry_id: int
    kind: ReflectionKind
    text: str
    sentiment: float
    triggered_crisis: bool = False
    triggered_recovery: bool = False


class ReflectionService:
    """Servizio stateless di riflessione."""

    @staticmethod
    def recent_entries(
        session: Session, character_id: int, *, limit: int = 10
    ) -> list[ReflectionEntry]:
        return list(
            session.scalars(
                select(ReflectionEntry)
                .where(ReflectionEntry.character_id == character_id)
                .order_by(ReflectionEntry.at_total_seconds.desc())
                .limit(limit)
            )
        )

    @staticmethod
    def count(session: Session, character_id: int) -> int:
        return len(
            list(
                session.scalars(
                    select(ReflectionEntry).where(ReflectionEntry.character_id == character_id)
                )
            )
        )

    # ------------------------------------------------------------------
    # Generate
    # ------------------------------------------------------------------

    @staticmethod
    def reflect(
        session: Session,
        character: Character,
        *,
        current_dt: AnthalysDateTime,
        rng: random.Random,
        kind: ReflectionKind | None = None,
    ) -> ReflectionResult:
        """Genera una riflessione. `kind` auto-rilevato se None."""
        if kind is None:
            kind = ReflectionService._pick_kind(session, character, current_dt)

        context = ReflectionService._build_context(session, character, current_dt)
        text, sentiment = compose_reflection(character, kind=kind, rng=rng, context=context)

        entry = ReflectionEntry(
            character_id=character.id,
            kind=kind.value,
            text=text,
            at_total_seconds=current_dt.to_total_seconds(),
            sentiment=sentiment,
            metadata_json=context,
        )
        session.add(entry)
        session.flush()

        # Effetti sul mood
        ReflectionService._apply_mood_effect(character, kind, sentiment)

        # Crea una memory (saliency bassa, non è un evento)
        MemoryService.record(
            session,
            owner_id=character.id,
            kind=MemoryKind.LONG_TERM,
            text=text,
            current_dt=current_dt,
            valence=sentiment,
            saliency=0.25 + 0.15 * abs(sentiment),
            tags=["reflection", kind.value.lower()],
        )

        logger.debug(
            "Reflection: char={} kind={} sent={:+.2f}",
            character.id,
            kind.value,
            sentiment,
        )
        return ReflectionResult(
            entry_id=entry.id,
            kind=kind,
            text=text,
            sentiment=sentiment,
        )

    # ------------------------------------------------------------------
    # Auto-detect kind
    # ------------------------------------------------------------------

    @staticmethod
    def _pick_kind(
        session: Session,
        character: Character,
        current_dt: AnthalysDateTime,
    ) -> ReflectionKind:
        mood = MoodState.from_dict(character.mood_json or {})
        stress, _ = StressService.compute(session, character, current_dt)

        if stress > 0.80:
            return ReflectionKind.CRISIS
        if mood.happiness < 0.35:
            return ReflectionKind.REGRET
        if mood.happiness > 0.70:
            # Random tra GRATITUDE, RESOLVE, OBSERVATION (pesi 40/30/30)
            import random

            rng_local = random.Random(
                hash((character.id, current_dt.to_total_seconds())) & 0xFFFFFFFF
            )
            roll = rng_local.random()
            if roll < 0.40:
                return ReflectionKind.GRATITUDE
            if roll < 0.70:
                return ReflectionKind.RESOLVE
            return ReflectionKind.OBSERVATION
        if stress < 0.40 and mood.happiness > 0.55:
            return ReflectionKind.RESOLVE
        return ReflectionKind.OBSERVATION

    @staticmethod
    def _build_context(
        session: Session,
        character: Character,
        current_dt: AnthalysDateTime,
    ) -> dict[str, object]:
        """Costruisce il contesto per i template."""
        context: dict[str, object] = {}

        # Memoria recente (ultima EMOTIONAL entro 30 giorni)
        cutoff = current_dt.to_total_seconds() - 30 * SECONDS_PER_DAY
        from simai.npc.memory.models import Memory

        recent = session.scalars(
            select(Memory)
            .where(
                Memory.owner_id == character.id,
                Memory.tick_total_seconds >= cutoff,
                Memory.kind == MemoryKind.EMOTIONAL.value,
            )
            .order_by(Memory.tick_total_seconds.desc())
            .limit(1)
        ).first()
        if recent is not None:
            context["memory_text"] = recent.text

        # Trait-based goal
        from simai.npc.traits.enums import Trait

        traits = set(character.traits_json or [])
        if Trait.AMBIZIOSO.value in traits:
            context["goal"] = "raggiungere i miei obiettivi"
        elif Trait.EMPATICO.value in traits:
            context["goal"] = "aiutare chi amo"
        elif Trait.CURIOSO.value in traits:
            context["goal"] = "scoprire qualcosa di nuovo"

        return context

    # ------------------------------------------------------------------
    # Mood effect
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_mood_effect(
        character: Character,
        kind: ReflectionKind,
        sentiment: float,
    ) -> None:
        """Piccolo boost o penalità al mood in base alla riflessione."""
        from simai.npc.mood import Moodlet

        delta = 0.0
        if kind is ReflectionKind.GRATITUDE:
            delta = +0.08
        elif kind is ReflectionKind.REGRET:
            delta = -0.05
        elif kind is ReflectionKind.RESOLVE:
            delta = +0.10
        elif kind is ReflectionKind.CRISIS:
            delta = -0.15
        elif kind is ReflectionKind.RECOVERY:
            delta = +0.12

        if delta == 0.0:
            return

        mood = MoodState.from_dict(character.mood_json or {})
        from simai.npc.needs.needs import Needs

        moodlet = Moodlet(
            name=f"Riflessione ({kind.value})",
            remaining_ticks=200,
            happiness_delta=delta,
            source="reflection",
        )
        new_mood = mood.tick(Needs.from_dict(character.needs_json or {}), (moodlet,))
        character.mood_json = new_mood.to_dict()


__all__ = ["ReflectionResult", "ReflectionService"]
