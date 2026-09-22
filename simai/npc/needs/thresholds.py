"""Soglie quantitative dei bisogni."""

from typing import Final

from simai.npc.needs.enums import NeedState

#: Soglia sotto cui un bisogno è critico.
CRITICAL_THRESHOLD: Final[float] = 10.0

#: Soglia sotto cui un bisogno è basso.
LOW_THRESHOLD: Final[float] = 30.0

#: Soglia sopra cui un bisogno è alto (ben soddisfatto).
HIGH_THRESHOLD: Final[float] = 70.0

#: Valore minimo/massimo di un bisogno.
MIN_NEED_VALUE: Final[float] = 0.0
MAX_NEED_VALUE: Final[float] = 100.0


def state_of(value: float) -> NeedState:
    """Ritorna lo stato qualitativo di un bisogno con valore `value`."""
    if value < CRITICAL_THRESHOLD:
        return NeedState.CRITICAL
    if value < LOW_THRESHOLD:
        return NeedState.LOW
    if value < HIGH_THRESHOLD:
        return NeedState.OK
    return NeedState.HIGH


__all__ = [
    "CRITICAL_THRESHOLD",
    "HIGH_THRESHOLD",
    "LOW_THRESHOLD",
    "MAX_NEED_VALUE",
    "MIN_NEED_VALUE",
    "state_of",
]
