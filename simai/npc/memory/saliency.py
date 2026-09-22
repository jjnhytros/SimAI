"""Calcolo della saliency di un evento (per la creazione di memorie)."""

from __future__ import annotations

from typing import Final

#: Peso dei bisogni critici sulla saliency.
CRITICAL_NEED_BOOST: Final[float] = 0.30

#: Peso di un moodlet forte (|delta| > 0.25).
STRONG_MOODLET_BOOST: Final[float] = 0.20

#: Peso di un evento sociale rilevante.
SOCIAL_EVENT_BOOST: Final[float] = 0.15

#: Peso di un evento di lifecycle (nascita/morte).
LIFECYCLE_BOOST: Final[float] = 0.50

#: Base minima di saliency.
BASE_SALIENCY: Final[float] = 0.20


def compute_saliency(
    *,
    base: float = BASE_SALIENCY,
    critical_needs: int = 0,
    strong_moodlets: int = 0,
    social_event: bool = False,
    lifecycle_event: bool = False,
) -> float:
    """Calcola la saliency in [0, 1] da una serie di contributi."""
    s = base
    s += CRITICAL_NEED_BOOST * critical_needs
    s += STRONG_MOODLET_BOOST * strong_moodlets
    if social_event:
        s += SOCIAL_EVENT_BOOST
    if lifecycle_event:
        s += LIFECYCLE_BOOST
    return max(0.0, min(1.0, s))


__all__ = [
    "BASE_SALIENCY",
    "CRITICAL_NEED_BOOST",
    "LIFECYCLE_BOOST",
    "SOCIAL_EVENT_BOOST",
    "STRONG_MOODLET_BOOST",
    "compute_saliency",
]
