"""LifeStageService — calcolo delle fasce di età e aspettativa di vita."""

from __future__ import annotations

from simai.config.anthalys import (
    LIFE_EXPECTANCY_FEMALE_MAX,
    LIFE_EXPECTANCY_FEMALE_MIN,
    LIFE_EXPECTANCY_MALE_MAX,
    LIFE_EXPECTANCY_MALE_MIN,
    LIFESTAGE_PEDIATRIC_THRESHOLDS,
    LIFESTAGE_PSYCHOSOCIAL_THRESHOLDS,
    SECONDS_PER_DAY,
    SECONDS_PER_YEAR,
)
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.npc.enums import LifeStagePediatric, LifeStagePsychosocial, Sex


def _stage_from_thresholds[E: (LifeStagePediatric, LifeStagePsychosocial)](
    age_seconds: int,
    thresholds: dict[str, int],
    enum_cls: type[E],
) -> E:
    """Ritorna la fascia in cui cade `age_seconds`, iterando dal threshold più alto."""
    if age_seconds < 0:
        raise ValueError(f"age_seconds non può essere negativo: {age_seconds}")
    for name, min_seconds in sorted(thresholds.items(), key=lambda kv: -kv[1]):
        if age_seconds >= min_seconds:
            return enum_cls(name)
    # Impossibile: il threshold più basso è 0 e age_seconds >= 0
    raise RuntimeError(f"Nessuna fascia trovata per age_seconds={age_seconds} in {thresholds}")


class LifeStageService:
    """Servizio stateless per il calcolo delle fasce di età."""

    @staticmethod
    def age_seconds_at(
        birth_total_seconds: int,
        current: AnthalysDateTime,
    ) -> int:
        """Secondi di età al tempo `current`."""
        return current.to_total_seconds() - birth_total_seconds

    @staticmethod
    def age_years_days(age_seconds: int) -> tuple[int, int]:
        """(anni, giorni) da `age_seconds`."""
        if age_seconds < 0:
            raise ValueError(f"age_seconds non può essere negativo: {age_seconds}")
        years, remaining = divmod(age_seconds, SECONDS_PER_YEAR)
        days = remaining // SECONDS_PER_DAY
        return years, days

    @staticmethod
    def get_pediatric_stage(age_seconds: int) -> LifeStagePediatric:
        """Fascia pediatrica/adolescenziale per `age_seconds`."""
        return _stage_from_thresholds(
            age_seconds, LIFESTAGE_PEDIATRIC_THRESHOLDS, LifeStagePediatric
        )

    @staticmethod
    def get_psychosocial_stage(age_seconds: int) -> LifeStagePsychosocial:
        """Fascia psicosociale per `age_seconds`."""
        return _stage_from_thresholds(
            age_seconds, LIFESTAGE_PSYCHOSOCIAL_THRESHOLDS, LifeStagePsychosocial
        )

    @staticmethod
    def get_life_expectancy(sex: Sex | str) -> tuple[int, int]:
        """(min, max) aspettativa di vita in anni Anthaliani per il sesso dato."""
        sex_str = sex.value if isinstance(sex, Sex) else sex
        if sex_str == Sex.FEMALE.value:
            return (LIFE_EXPECTANCY_FEMALE_MIN, LIFE_EXPECTANCY_FEMALE_MAX)
        if sex_str == Sex.MALE.value:
            return (LIFE_EXPECTANCY_MALE_MIN, LIFE_EXPECTANCY_MALE_MAX)
        # Intersex o sconosciuto: media tra M e F
        return (
            (LIFE_EXPECTANCY_MALE_MIN + LIFE_EXPECTANCY_FEMALE_MIN) // 2,
            (LIFE_EXPECTANCY_MALE_MAX + LIFE_EXPECTANCY_FEMALE_MAX) // 2,
        )


__all__ = ["LifeStageService"]
