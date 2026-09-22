"""Enum del dominio riflessione/narrazione."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class ReflectionKind(StrEnum):
    """Tipo di entry del diario."""

    GRATITUDE = "GRATITUDE"  # cose positive
    REGRET = "REGRET"  # rimpianti
    RESOLVE = "RESOLVE"  # propositi
    OBSERVATION = "OBSERVATION"  # osservazioni neutre
    CRISIS = "CRISIS"  # crisi cosciente
    RECOVERY = "RECOVERY"  # recupero post-crisi


class CrisisPhase(StrEnum):
    """Fase di una crisi cosciente."""

    ACTIVE = "ACTIVE"
    RESOLVING = "RESOLVING"
    RESOLVED = "RESOLVED"


#: Intervallo (giorni) tra riflessioni automatiche.
REFLECTION_INTERVAL_DAYS: Final[int] = 7

#: Numero di riflessioni negative consecutive per crisi.
NEGATIVE_STREAK_FOR_CRISIS: Final[int] = 3

#: Stress threshold per crisi.
STRESS_CRISIS_THRESHOLD: Final[float] = 0.85

#: Giorni consecutivi sopra soglia stress per crisi.
STRESS_DAYS_FOR_CRISIS: Final[int] = 3

#: Durata minima (giorni) di una crisi.
MIN_CRISIS_DURATION_DAYS: Final[int] = 5

#: Soglia di stress per uscire da crisi.
RECOVERY_STRESS_THRESHOLD: Final[float] = 0.50

#: Soglia di happiness per uscire da crisi.
RECOVERY_HAPPINESS_THRESHOLD: Final[float] = 0.55

#: Effetti della crisi.
CRISIS_INHIBITION_DELTA: Final[float] = +0.15
CRISIS_COMFORT_DELTA: Final[float] = -0.15

#: Moodlet delta in crisi.
CRISIS_MOODLET_DELTA: Final[float] = -0.20

#: Moodlet delta in recovery.
RECOVERY_MOODLET_DELTA: Final[float] = +0.10


__all__ = [
    "CRISIS_COMFORT_DELTA",
    "CRISIS_INHIBITION_DELTA",
    "CRISIS_MOODLET_DELTA",
    "MIN_CRISIS_DURATION_DAYS",
    "NEGATIVE_STREAK_FOR_CRISIS",
    "RECOVERY_HAPPINESS_THRESHOLD",
    "RECOVERY_MOODLET_DELTA",
    "RECOVERY_STRESS_THRESHOLD",
    "REFLECTION_INTERVAL_DAYS",
    "STRESS_CRISIS_THRESHOLD",
    "STRESS_DAYS_FOR_CRISIS",
    "CrisisPhase",
    "ReflectionKind",
]
