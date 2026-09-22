"""Enum e costanti del dominio vizi e dipendenze."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class AddictionKind(StrEnum):
    """Tipi di dipendenza."""

    ALCOHOL = "ALCOHOL"
    TOBACCO = "TOBACCO"
    GAMBLING = "GAMBLING"
    CAFFEINE = "CAFFEINE"
    INTIMACY = "INTIMACY"


#: Dipendenza minima sotto cui l'addiction viene rimossa.
MIN_DEPENDENCE: Final[float] = 5.0

#: Dipendenza massima.
MAX_DEPENDENCE: Final[float] = 100.0

#: Dipendenza iniziale quando si inizia una nuova addiction.
INITIAL_DEPENDENCE: Final[dict[AddictionKind, float]] = {
    AddictionKind.ALCOHOL: 15.0,
    AddictionKind.TOBACCO: 20.0,
    AddictionKind.GAMBLING: 10.0,
    AddictionKind.CAFFEINE: 10.0,
    AddictionKind.INTIMACY: 8.0,
}

#: Incremento di dipendenza per singolo uso.
DEPENDENCE_PER_USE: Final[dict[AddictionKind, float]] = {
    AddictionKind.ALCOHOL: 2.0,
    AddictionKind.TOBACCO: 3.0,
    AddictionKind.GAMBLING: 2.5,
    AddictionKind.CAFFEINE: 1.5,
    AddictionKind.INTIMACY: 1.0,
}

#: Incremento di tolleranza per singolo uso.
TOLERANCE_PER_USE: Final[float] = 0.5

#: Probabilità di iniziare una dipendenza al primo uso.
INITIATION_PROBABILITY: Final[dict[AddictionKind, float]] = {
    AddictionKind.ALCOHOL: 0.15,
    AddictionKind.TOBACCO: 0.20,
    AddictionKind.GAMBLING: 0.10,
    AddictionKind.CAFFEINE: 0.05,
    AddictionKind.INTIMACY: 0.03,
}

#: Soglie di craving (dipendenza minima per attivare).
CRAVING_THRESHOLD_MILD: Final[float] = 30.0
CRAVING_THRESHOLD_STRONG: Final[float] = 60.0
CRAVING_THRESHOLD_WITHDRAWAL: Final[float] = 80.0

#: Giorni di inattività richiesti per attivare ogni livello.
DAYS_FOR_MILD_CRAVING: Final[int] = 1
DAYS_FOR_STRONG_CRAVING: Final[int] = 2
DAYS_FOR_WITHDRAWAL: Final[int] = 3

#: Delta happiness dei moodlet (per giorno).
MOODLET_MILD_DELTA: Final[float] = -0.05
MOODLET_STRONG_DELTA: Final[float] = -0.15
MOODLET_WITHDRAWAL_DELTA: Final[float] = -0.30

#: Giorni di inattività prima del decay della dipendenza.
DECAY_GRACE_DAYS: Final[int] = 90

#: Dipendenza persa per giorno dopo la grazia.
DECAY_RATE_PER_DAY: Final[float] = 0.10

#: Moltiplicatore del boost di utility per craving.
CRAVING_BOOST_FACTOR: Final[float] = 0.4

#: Età minima per iniziare una dipendenza.
MIN_INITIATION_AGE_YEARS: Final[int] = 16


#: Durata (in tick Anthalys) del moodlet di craving/withdrawal.
#: 1 giorno Anthalys = 336 tick (28h × 60m / 5min).
MOODLET_DURATION_TICKS: Final[int] = 336


__all__ = [
    "CRAVING_BOOST_FACTOR",
    "CRAVING_THRESHOLD_MILD",
    "CRAVING_THRESHOLD_STRONG",
    "CRAVING_THRESHOLD_WITHDRAWAL",
    "DAYS_FOR_MILD_CRAVING",
    "DAYS_FOR_STRONG_CRAVING",
    "DAYS_FOR_WITHDRAWAL",
    "DECAY_GRACE_DAYS",
    "DECAY_RATE_PER_DAY",
    "DEPENDENCE_PER_USE",
    "INITIAL_DEPENDENCE",
    "INITIATION_PROBABILITY",
    "MAX_DEPENDENCE",
    "MIN_DEPENDENCE",
    "MIN_INITIATION_AGE_YEARS",
    "MOODLET_DURATION_TICKS",
    "MOODLET_MILD_DELTA",
    "MOODLET_STRONG_DELTA",
    "MOODLET_WITHDRAWAL_DELTA",
    "TOLERANCE_PER_USE",
    "AddictionKind",
]
