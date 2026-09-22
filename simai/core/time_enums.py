"""Enum del dominio temporale di Anthalys."""

from enum import StrEnum


class DayPhase(StrEnum):
    """Fasi della giornata Anthalys (7 fasi su 28 ore).

    Le boundary orarie sono definite in `config.anthalys.DAY_PHASE_BOUNDARIES`.
    """

    DEEP_NIGHT = "DEEP_NIGHT"
    DAWN = "DAWN"
    MORNING = "MORNING"
    NOON = "NOON"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class Season(StrEnum):
    """Stagioni di Anthalys (4 stagioni da 108 giorni ciascuna).

    L'inverno inizia il giorno 16 del mese 18 (day-of-year = 424).
    """

    WINTER = "Inverno"
    SPRING = "Primavera"
    SUMMER = "Estate"
    AUTUMN = "Autunno"
