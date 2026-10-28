from enum import StrEnum


class LocationKind(StrEnum):
    RESIDENTIAL = "residential"
    SOCIAL = "social"
    LEISURE = "leisure"


class DeathCause(StrEnum):
    OLD_AGE = "old_age"
    ILLNESS = "illness"
    ACCIDENT = "accident"
    VIOLENCE = "violence"
    UNKNOWN = "unknown"
    MANUAL = "manual"


class LifeStage(StrEnum):
    EARLY_CHILDHOOD = "early_childhood"
    CHILDHOOD = "childhood"
    EARLY_ADOLESCENCE = "early_adolescence"
    LATE_ADOLESCENCE = "late_adolescence"
    YOUNG_ADULT = "young_adult"
    EARLY_ADULTHOOD = "early_adulthood"
    MIDDLE_ADULTHOOD = "middle_adulthood"
    LATE_ADULTHOOD = "late_adulthood"
    SENIORITY = "seniority"
