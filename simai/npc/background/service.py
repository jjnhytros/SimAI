"""BackgroundService — registrazione eventi formativi + effetti identità."""

from __future__ import annotations

import random
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.background.enums import (
    BULLY_TIMID_THRESHOLD,
    DEFAULT_TEXTS,
    EVENT_VALENCE,
    MAX_SEED_EVENTS,
    MEMORY_THRESHOLD,
    SEVERITY_RANGES,
    FormativeEventKind,
)
from simai.npc.background.models import FormativeEvent
from simai.npc.identity import IdentityService
from simai.npc.memory.enums import MemoryKind
from simai.npc.memory.service import MemoryService
from simai.npc.models import Character
from simai.npc.traits.derivation import names_to_traits, traits_to_names
from simai.npc.traits.enums import Trait


@dataclass(frozen=True, slots=True)
class SeedEvent:
    """Evento formativo "astratto" generato dal seed (non persistito)."""

    kind: FormativeEventKind
    occurred_at_age: int
    severity: float
    text: str


class BackgroundService:
    """Servizio stateless per il background narrativo."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def all_of(session: Session, character_id: int) -> list[FormativeEvent]:
        """Tutti gli eventi formativi del character, ordinati per età."""
        return list(
            session.scalars(
                select(FormativeEvent)
                .where(FormativeEvent.character_id == character_id)
                .order_by(FormativeEvent.occurred_at_age)
            )
        )

    @staticmethod
    def count(session: Session, character_id: int) -> int:
        return len(BackgroundService.all_of(session, character_id))

    # ------------------------------------------------------------------
    # Record event
    # ------------------------------------------------------------------

    @staticmethod
    def record_event(
        session: Session,
        *,
        character: Character,
        kind: FormativeEventKind,
        occurred_at_age: int,
        severity: float,
        text: str | None = None,
        current_dt: AnthalysDateTime,
        metadata: dict[str, object] | None = None,
    ) -> FormativeEvent | None:
        """Crea un evento formativo + applica gli effetti.

        Ritorna `None` se l'evento esiste già (unique constraint).
        """
        if occurred_at_age < 0:
            raise ValueError(f"occurred_at_age deve essere >= 0, ricevuto {occurred_at_age}")
        if not (0.0 <= severity <= 1.0):
            raise ValueError(f"severity deve essere in [0, 1], ricevuto {severity}")

        # Verifica duplicato
        existing = session.scalars(
            select(FormativeEvent).where(
                FormativeEvent.character_id == character.id,
                FormativeEvent.kind == kind.value,
                FormativeEvent.occurred_at_age == occurred_at_age,
            )
        ).first()
        if existing is not None:
            return None

        occurred_secs = character.birth_total_seconds + occurred_at_age * SECONDS_PER_YEAR
        event = FormativeEvent(
            character_id=character.id,
            kind=kind.value,
            occurred_at_age=occurred_at_age,
            occurred_at_total_seconds=occurred_secs,
            severity=severity,
            text=text or DEFAULT_TEXTS.get(kind, kind.value),
            metadata_json=dict(metadata or {}),
        )
        session.add(event)
        session.flush()

        # Applica effetti su identity
        BackgroundService._apply_identity_effects(character, kind=kind, severity=severity)

        # Personality (Chunk 3.6d)
        from simai.npc.personality import PersonalityService

        PersonalityService.apply_event(character, kind=kind, severity=severity)

        # Forza tratto se necessario
        BackgroundService._maybe_force_trait(character, kind=kind, severity=severity)

        # Crea memoria se severity alta
        if severity >= MEMORY_THRESHOLD:
            BackgroundService._maybe_create_memory(
                session,
                character=character,
                kind=kind,
                severity=severity,
                text=event.text,
                occurred_secs=occurred_secs,
            )

        logger.debug(
            "Formative event: char={} {} age={} sev={:.2f}",
            character.id,
            kind.value,
            occurred_at_age,
            severity,
        )
        return event

    # ------------------------------------------------------------------
    # Effetti
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_identity_effects(
        character: Character,
        *,
        kind: FormativeEventKind,
        severity: float,
    ) -> None:
        """Applica effetti di SEP/inhibition/comfort sul character."""
        # BULLIED: inibizione +, comfort -
        if kind is FormativeEventKind.BULLIED:
            IdentityService.add_sep_inhibition(character, +0.05 + 0.10 * severity)
            IdentityService.add_sep_comfort(character, -(0.05 + 0.10 * severity))
            return

        # TRAUMA: effetti forti
        if kind is FormativeEventKind.TRAUMA:
            IdentityService.add_sep_inhibition(character, +0.10 + 0.15 * severity)
            IdentityService.add_sep_comfort(character, -(0.10 + 0.15 * severity))
            return

        # BETRAYAL: inibizione +, comfort -
        if kind is FormativeEventKind.BETRAYAL:
            IdentityService.add_sep_inhibition(character, +0.05 + 0.05 * severity)
            IdentityService.add_sep_comfort(character, -(0.05 + 0.05 * severity))
            return

        # FIRST_LOVE: comfort +, inhibition -
        if kind is FormativeEventKind.FIRST_LOVE:
            IdentityService.add_sep_comfort(character, +0.03 + 0.05 * severity)
            IdentityService.add_sep_inhibition(character, -(0.02 + 0.03 * severity))
            return

        # MENTORSHIP: knowledge +
        if kind is FormativeEventKind.MENTORSHIP:
            IdentityService.add_sep_knowledge(character, +5.0 + 10.0 * severity)
            return

        # PARENT_LOST: leggero aumento inibizione
        if kind is FormativeEventKind.PARENT_LOST:
            IdentityService.add_sep_inhibition(character, +0.05 * severity)
            return

    @staticmethod
    def _maybe_force_trait(
        character: Character,
        *,
        kind: FormativeEventKind,
        severity: float,
    ) -> None:
        """Aggiunge `TIMIDO` se BULLIED severo e non già presente."""
        if kind is not FormativeEventKind.BULLIED:
            return
        if severity < BULLY_TIMID_THRESHOLD:
            return
        current = names_to_traits(character.traits_json or [])
        if Trait.TIMIDO in current:
            return
        current.append(Trait.TIMIDO)
        character.traits_json = traits_to_names(current)

    @staticmethod
    def _maybe_create_memory(
        session: Session,
        *,
        character: Character,
        kind: FormativeEventKind,
        severity: float,
        text: str,
        occurred_secs: int,
    ) -> None:
        """Crea una `Memory` di tipo EMOTIONAL se severity >= soglia."""
        valence = EVENT_VALENCE.get(kind, 0.0)
        saliency = 0.5 + 0.4 * severity
        occurred_dt = AnthalysDateTime.from_total_seconds(occurred_secs)
        MemoryService.record(
            session,
            owner_id=character.id,
            kind=MemoryKind.EMOTIONAL,
            text=text,
            current_dt=occurred_dt,
            valence=valence,
            saliency=saliency,
            tags=["formative", kind.value.lower()],
            lifecycle_event=True,
        )

    # ------------------------------------------------------------------
    # Seed generation
    # ------------------------------------------------------------------

    @staticmethod
    def generate_seed_events(
        rng: random.Random,
        *,
        age_years: int,
    ) -> list[SeedEvent]:
        """Genera 1-3 eventi formativi "verosimili" per un NPC al seed."""
        if age_years < 1:
            return []

        events: list[SeedEvent] = []

        # Evento "baseline" (tutti gli NPC con infanzia)
        if age_years >= 5:
            events.append(
                BackgroundService._make_event(
                    rng,
                    kind=FormativeEventKind.MOVED,
                    max_age=age_years,
                    min_age=2,
                )
            )

        # BULLIED: 30% dei casi, solo se non ancora adulti
        if age_years >= 7 and rng.random() < 0.30:
            events.append(
                BackgroundService._make_event(
                    rng,
                    kind=FormativeEventKind.BULLIED,
                    max_age=min(age_years, 18),
                    min_age=6,
                )
            )

        # ILLNESS: 20%
        if age_years >= 3 and rng.random() < 0.20:
            events.append(
                BackgroundService._make_event(
                    rng,
                    kind=FormativeEventKind.ILLNESS,
                    max_age=age_years,
                    min_age=2,
                )
            )

        # FIRST_LOVE: 50% degli adolescenti/adulti
        if age_years >= 12 and rng.random() < 0.50:
            events.append(
                BackgroundService._make_event(
                    rng,
                    kind=FormativeEventKind.FIRST_LOVE,
                    max_age=min(age_years, 20),
                    min_age=12,
                )
            )

        # MENTORSHIP: 25% degli adulti
        if age_years >= 18 and rng.random() < 0.25:
            events.append(
                BackgroundService._make_event(
                    rng,
                    kind=FormativeEventKind.MENTORSHIP,
                    max_age=age_years,
                    min_age=15,
                )
            )

        # TRAUMA: 10% degli adulti
        if age_years >= 18 and rng.random() < 0.10:
            events.append(
                BackgroundService._make_event(
                    rng,
                    kind=FormativeEventKind.TRAUMA,
                    max_age=age_years,
                    min_age=5,
                )
            )

        # Cap
        return events[:MAX_SEED_EVENTS]

    @staticmethod
    def _make_event(
        rng: random.Random,
        *,
        kind: FormativeEventKind,
        max_age: int,
        min_age: int,
    ) -> SeedEvent:
        """Costruisce un `SeedEvent` con età e severity casuali nel range."""
        if max_age < min_age:
            max_age = min_age
        age_at = rng.randint(min_age, max_age)
        lo, hi = SEVERITY_RANGES.get(kind, (0.3, 0.7))
        severity = rng.uniform(lo, hi)
        return SeedEvent(
            kind=kind,
            occurred_at_age=age_at,
            severity=severity,
            text=DEFAULT_TEXTS.get(kind, kind.value),
        )

    # ------------------------------------------------------------------
    # Persistenza di un set di eventi seed
    # ------------------------------------------------------------------

    @staticmethod
    def persist_seed_events(
        session: Session,
        *,
        character: Character,
        events: list[SeedEvent],
        current_dt: AnthalysDateTime,
    ) -> int:
        """Persiste gli eventi seed sul character. Ritorna il numero creati."""
        created = 0
        for ev in events:
            result = BackgroundService.record_event(
                session,
                character=character,
                kind=ev.kind,
                occurred_at_age=ev.occurred_at_age,
                severity=ev.severity,
                text=ev.text,
                current_dt=current_dt,
            )
            if result is not None:
                created += 1
        return created


__all__ = ["BackgroundService", "SeedEvent"]
