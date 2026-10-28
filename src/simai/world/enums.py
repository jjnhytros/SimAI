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
