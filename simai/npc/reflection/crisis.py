"""CrisisService — crollo cosciente e recupero post-trauma."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.identity import IdentityService
from simai.npc.models import Character
from simai.npc.mood import Moodlet, MoodState
from simai.npc.needs.needs import Needs
from simai.npc.reflection.enums import (
    CRISIS_COMFORT_DELTA,
    CRISIS_INHIBITION_DELTA,
    CRISIS_MOODLET_DELTA,
    MIN_CRISIS_DURATION_DAYS,
    NEGATIVE_STREAK_FOR_CRISIS,
    RECOVERY_HAPPINESS_THRESHOLD,
    RECOVERY_MOODLET_DELTA,
    RECOVERY_STRESS_THRESHOLD,
    STRESS_CRISIS_THRESHOLD,
    STRESS_DAYS_FOR_CRISIS,
    CrisisPhase,
)
from simai.npc.stress.service import StressService


@dataclass(frozen=True, slots=True)
class CrisisStatus:
    """Stato di crisi di un character."""

    active: bool
    phase: CrisisPhase
    started_at: int | None
    days_in_crisis: int
    reason: str


class CrisisService:
    """Servizio stateless di gestione crisi coscienti."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get_status(character: Character) -> CrisisStatus:
        attrs = character.attributes_json or {}
        crisis = attrs.get("crisis")
        if not isinstance(crisis, dict) or not crisis:
            return CrisisStatus(False, CrisisPhase.RESOLVED, None, 0, "")
        phase_str = str(crisis.get("phase", CrisisPhase.RESOLVED.value))
        try:
            phase = CrisisPhase(phase_str)
        except ValueError:
            phase = CrisisPhase.RESOLVED
        return CrisisStatus(
            active=phase is CrisisPhase.ACTIVE,
            phase=phase,
            started_at=crisis.get("started_at")
            if isinstance(crisis.get("started_at"), int)
            else None,
            days_in_crisis=int(crisis.get("days_in_crisis", 0)),
            reason=str(crisis.get("reason", "")),
        )

    # ------------------------------------------------------------------
    # Trigger check (daily)
    # ------------------------------------------------------------------

    @staticmethod
    def check_trigger(
        session: Session,
        character: Character,
        *,
        current_dt: AnthalysDateTime,
        recent_negative_streak: int,
    ) -> tuple[bool, str]:
        """Valuta se scatenare una crisi. Ritorna `(should_trigger, reason)`."""
        status = CrisisService.get_status(character)
        if status.active:
            return False, "already_active"

        stress, _ = StressService.compute(session, character, current_dt)
        if stress >= STRESS_CRISIS_THRESHOLD:
            attrs = dict(character.attributes_json or {})
            stress_days = int(attrs.get("_stress_days_above", 0)) + 1
            attrs["_stress_days_above"] = stress_days
            character.attributes_json = attrs
            if stress_days >= STRESS_DAYS_FOR_CRISIS:
                return True, f"stress_persistent ({stress:.2f})"
        else:
            attrs = dict(character.attributes_json or {})
            attrs["_stress_days_above"] = 0
            character.attributes_json = attrs

        if recent_negative_streak >= NEGATIVE_STREAK_FOR_CRISIS:
            return True, f"negative_streak ({recent_negative_streak})"

        return False, "no_trigger"

    # ------------------------------------------------------------------
    # Start / resolve
    # ------------------------------------------------------------------

    @staticmethod
    def start_crisis(
        character: Character,
        *,
        reason: str,
        current_dt: AnthalysDateTime,
    ) -> bool:
        """Attiva una crisi. Ritorna True se attivata."""
        status = CrisisService.get_status(character)
        if status.active:
            return False

        attrs = dict(character.attributes_json or {})
        attrs["crisis"] = {
            "phase": CrisisPhase.ACTIVE.value,
            "started_at": current_dt.to_total_seconds(),
            "days_in_crisis": 0,
            "reason": reason,
        }
        character.attributes_json = attrs

        # Effetti: inhibition +, comfort -
        IdentityService.add_sep_inhibition(character, CRISIS_INHIBITION_DELTA)
        IdentityService.add_sep_comfort(character, CRISIS_COMFORT_DELTA)

        # Moodlet crisi
        CrisisService._apply_moodlet(
            character, "Crisi cosciente", CRISIS_MOODLET_DELTA, duration=500
        )

        # Personality shift (Chunk 3.6d)
        from simai.npc.background.enums import FormativeEventKind
        from simai.npc.personality import PersonalityService

        PersonalityService.apply_event(
            character,
            kind=FormativeEventKind.TRAUMA,
            severity=0.80,
        )

        logger.info("Crisis started: char={} reason={}", character.id, reason)
        return True

    @staticmethod
    def recovery_tick(
        session: Session,
        character: Character,
        *,
        current_dt: AnthalysDateTime,
    ) -> str:
        """Applica un giorno di recupero. Ritorna la nuova phase."""
        status = CrisisService.get_status(character)
        if not status.active:
            return CrisisPhase.RESOLVED.value

        attrs = dict(character.attributes_json or {})
        crisis = dict(attrs.get("crisis", {}))
        days = int(crisis.get("days_in_crisis", 0)) + 1
        crisis["days_in_crisis"] = days

        mood = MoodState.from_dict(character.mood_json or {})
        stress, _ = StressService.compute(session, character, current_dt)

        # Condizioni di recupero: min duration + stress basso + mood buono
        can_resolve = (
            days >= MIN_CRISIS_DURATION_DAYS
            and stress < RECOVERY_STRESS_THRESHOLD
            and mood.happiness > RECOVERY_HAPPINESS_THRESHOLD
        )

        if can_resolve:
            # Personality shift positivo (Chunk 3.6d)
            from simai.npc.background.enums import FormativeEventKind
            from simai.npc.personality import PersonalityService

            PersonalityService.apply_event(
                character,
                kind=FormativeEventKind.ACHIEVEMENT,
                severity=0.40,
            )
            crisis["phase"] = CrisisPhase.RESOLVED.value
            crisis["resolved_at"] = current_dt.to_total_seconds()
            CrisisService._apply_moodlet(
                character, "Rinascita", RECOVERY_MOODLET_DELTA, duration=400
            )
            # Riduce inhibition e aumenta comfort (contrario della crisi)
            IdentityService.add_sep_inhibition(character, -CRISIS_INHIBITION_DELTA * 0.5)
            IdentityService.add_sep_comfort(character, -CRISIS_COMFORT_DELTA * 0.5)
            logger.info(
                "Crisis resolved: char={} after {} days",
                character.id,
                days,
            )
        else:
            crisis["phase"] = CrisisPhase.RESOLVING.value

        new_phase: str = str(crisis["phase"])
        attrs["crisis"] = crisis
        character.attributes_json = attrs
        return new_phase

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_moodlet(
        character: Character,
        name: str,
        delta: float,
        *,
        duration: int,
    ) -> None:
        mood = MoodState.from_dict(character.mood_json or {})
        moodlet = Moodlet(
            name=name,
            remaining_ticks=duration,
            happiness_delta=delta,
            source="crisis",
        )
        new_mood = mood.tick(Needs.from_dict(character.needs_json or {}), (moodlet,))
        character.mood_json = new_mood.to_dict()


__all__ = ["CrisisService", "CrisisStatus"]
