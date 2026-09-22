"""DesireService — calcolo e refresh del desiderio."""

from __future__ import annotations

import random
from typing import Final

from sqlalchemy.orm import Session

from simai.config.anthalys import SECONDS_PER_DAY, SECONDS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.desire.models import DesireState
from simai.npc.identity import IdentityService
from simai.npc.lifestage_service import LifeStageService
from simai.npc.models import Character
from simai.npc.mood import MoodState
from simai.npc.stress.service import StressService

#: Soglia sotto cui il desiderio è considerato "asessuale".
ASEXUAL_THRESHOLD: Final[float] = 0.15

#: Massimo boost da astinenza.
MAX_ABSTINENCE_DAYS: Final[float] = 10.0


class DesireService:
    """Servizio stateless di gestione del desiderio."""

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    @staticmethod
    def initialize(
        character: Character,
        rng: random.Random,
        *,
        current_dt: AnthalysDateTime,
    ) -> DesireState:
        """Inizializza il desire da sexuality del character."""
        sexuality = IdentityService.get_sexuality(character)
        avg_attraction = (
            sexuality.attraction_to_male
            + sexuality.attraction_to_female
            + sexuality.attraction_to_nonbinary
        ) / 3.0
        # Mappa [0, 1] -> [0.1, 0.9] con jitter
        baseline = 0.1 + 0.8 * avg_attraction
        baseline = max(0.1, min(0.9, baseline + rng.uniform(-0.05, 0.05)))
        return DesireState(
            baseline=baseline,
            current=baseline,
            last_satisfied_at=current_dt.to_total_seconds(),
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get_state(character: Character) -> DesireState:
        data = (character.attributes_json or {}).get("desire")
        return DesireState.from_dict(data) if isinstance(data, dict) else DesireState()

    @staticmethod
    def get_current(character: Character) -> float:
        return DesireService.get_state(character).current

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @staticmethod
    def recompute(
        session: Session,
        character: Character,
        *,
        current_dt: AnthalysDateTime,
    ) -> DesireState:
        """Ricalcola `current` da baseline + età + stress + mood + astinenza."""
        state = DesireService.get_state(character)
        current_secs = current_dt.to_total_seconds()

        # Età
        age_secs = LifeStageService.age_seconds_at(character.birth_total_seconds, current_dt)
        age_years = int(age_secs // SECONDS_PER_YEAR)
        age_peak = DesireService._age_peak(age_years)

        # Astinenza
        days_since = (current_secs - state.last_satisfied_at) / SECONDS_PER_DAY
        abstinence_factor = 0.5 + 0.5 * min(days_since, MAX_ABSTINENCE_DAYS) / MAX_ABSTINENCE_DAYS

        # Stress
        stress, _ = StressService.compute(session, character, current_dt)
        stress_factor = 1.0 - 0.7 * stress

        # Mood
        mood = MoodState.from_dict(character.mood_json or {})
        mood_factor = 0.5 + 0.5 * mood.happiness

        # Refractory (breve: 2 ore Anthalys = 1/14 giorno)
        refractory = 0.5 if days_since < (1.0 / 14.0) else 1.0

        current = (
            state.baseline * age_peak * abstinence_factor * stress_factor * mood_factor * refractory
        )
        current = max(0.0, min(1.0, current))

        new_state = DesireState(
            baseline=state.baseline,
            current=current,
            last_satisfied_at=state.last_satisfied_at,
        )
        DesireService.write_state(character, new_state)
        return new_state

    @staticmethod
    def mark_satisfied(character: Character, current_dt: AnthalysDateTime) -> None:
        """Registra un soddisfacimento (chiamato da IntimacyService)."""
        state = DesireService.get_state(character)
        new_state = DesireState(
            baseline=state.baseline,
            current=state.current,
            last_satisfied_at=current_dt.to_total_seconds(),
        )
        DesireService.write_state(character, new_state)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _age_peak(age_years: int) -> float:
        """Fattore età: 0.3 sotto 6, 1.0 tra 18 e 40, cala dopo."""
        if age_years < 6:
            return 0.30
        if age_years < 18:
            # 0.3 -> 1.0 lineare
            return 0.30 + 0.70 * (age_years - 6) / 12.0
        if age_years <= 40:
            return 1.00
        if age_years <= 70:
            # 1.0 -> 0.30 lineare
            return 1.00 - 0.70 * (age_years - 40) / 30.0
        return 0.30

    @staticmethod
    def write_state(character: Character, state: DesireState) -> None:
        attrs = dict(character.attributes_json or {})
        attrs["desire"] = state.to_dict()
        character.attributes_json = attrs


__all__ = ["ASEXUAL_THRESHOLD", "MAX_ABSTINENCE_DAYS", "DesireService"]
