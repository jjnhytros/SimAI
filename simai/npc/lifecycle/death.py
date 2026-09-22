"""DeathService — mortalità e registrazione morte."""

from __future__ import annotations

from typing import Final

from sqlalchemy.orm import Session

from simai.config.anthalys import (
    LIFE_EXPECTANCY_FEMALE_MAX,
    LIFE_EXPECTANCY_FEMALE_MIN,
    LIFE_EXPECTANCY_MALE_MAX,
    LIFE_EXPECTANCY_MALE_MIN,
)
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.enums import Sex
from simai.npc.lifecycle.enums import DeathCause
from simai.npc.models import Character

#: Baseline giornaliera di mortalità (prima dell'aspettativa minima).
BASELINE_DAILY_MORTALITY: Final[float] = 1e-5

#: Mortalità giornaliera raggiunta a `exp_max`.
MAX_DAILY_MORTALITY: Final[float] = 1.0 / 30.0

#: Moltiplicatore per cause "non naturali" (incidenti).
ACCIDENT_SHARE_OF_DEATHS: Final[float] = 0.15


class DeathService:
    """Calcolo della probabilità di morte e registrazione."""

    @staticmethod
    def life_expectancy(sex: str) -> tuple[int, int]:
        """(min, max) aspettativa di vita in anni Anthalys per il sesso."""
        if sex == Sex.FEMALE.value:
            return (LIFE_EXPECTANCY_FEMALE_MIN, LIFE_EXPECTANCY_FEMALE_MAX)
        if sex == Sex.MALE.value:
            return (LIFE_EXPECTANCY_MALE_MIN, LIFE_EXPECTANCY_MALE_MAX)
        # Intersex / sconosciuto: media
        return (
            (LIFE_EXPECTANCY_MALE_MIN + LIFE_EXPECTANCY_FEMALE_MIN) // 2,
            (LIFE_EXPECTANCY_MALE_MAX + LIFE_EXPECTANCY_FEMALE_MAX) // 2,
        )

    @staticmethod
    def mortality_probability_per_day(age_years: int, sex: str) -> float:
        """Probabilità giornaliera di morte per un individuo di età data.

        Modello:
          - `age < exp_min`: baseline `BASELINE_DAILY_MORTALITY`
          - `exp_min <= age < exp_max`: rampa cubica da baseline a MAX_DAILY_MORTALITY
          - `age >= exp_max`: MAX_DAILY_MORTALITY
        """
        if age_years < 0:
            raise ValueError(f"age_years non può essere negativo: {age_years}")
        exp_min, exp_max = DeathService.life_expectancy(sex)
        if age_years < exp_min:
            return BASELINE_DAILY_MORTALITY
        if age_years >= exp_max:
            return MAX_DAILY_MORTALITY
        t = (age_years - exp_min) / (exp_max - exp_min)
        return BASELINE_DAILY_MORTALITY + (MAX_DAILY_MORTALITY - BASELINE_DAILY_MORTALITY) * (t**3)

    @staticmethod
    def pick_cause(age_years: int, sex: str, *, random_value: float) -> DeathCause:
        """Determina la causa di morte.

        `random_value` è in [0, 1) — fornito per testabilità.
        """
        exp_min, _exp_max = DeathService.life_expectancy(sex)
        if age_years >= exp_min:
            # Vecchiaia
            if random_value < (1.0 - ACCIDENT_SHARE_OF_DEATHS):
                return DeathCause.OLD_AGE
            return DeathCause.ACCIDENT
        # Giovane: malattia o incidente
        if random_value < 0.7:
            return DeathCause.ILLNESS
        return DeathCause.ACCIDENT

    @staticmethod
    def register_death(
        session: Session,
        character: Character,
        current_dt: AnthalysDateTime,
        cause: DeathCause,
    ) -> None:
        """Registra la morte di un Character nel DB."""
        if not character.is_alive:
            return
        character.is_alive = False
        character.death_total_seconds = current_dt.to_total_seconds()
        character.death_iso = current_dt.to_iso_string()
        character.death_cause = cause.value
        session.flush()


__all__ = [
    "ACCIDENT_SHARE_OF_DEATHS",
    "BASELINE_DAILY_MORTALITY",
    "MAX_DAILY_MORTALITY",
    "DeathService",
]
