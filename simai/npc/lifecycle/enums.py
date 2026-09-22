"""Enum del dominio ciclo vita."""

from enum import StrEnum


class DeathCause(StrEnum):
    """Causa di morte di un Character."""

    OLD_AGE = "OLD_AGE"
    ILLNESS = "ILLNESS"
    ACCIDENT = "ACCIDENT"
    CHILDBIRTH = "CHILDBIRTH"
    STARVATION = "STARVATION"
    UNKNOWN = "UNKNOWN"


class PregnancyStatus(StrEnum):
    """Stato di una gravidanza."""

    ACTIVE = "ACTIVE"
    DELIVERED = "DELIVERED"
    ABORTED = "ABORTED"


__all__ = ["DeathCause", "PregnancyStatus"]
