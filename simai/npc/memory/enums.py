"""Enum del dominio memoria."""

from enum import StrEnum


class MemoryKind(StrEnum):
    """Tipo di memoria."""

    SHORT_TERM = "SHORT_TERM"  # ultime ore, decade in pochi giorni
    LONG_TERM = "LONG_TERM"  # mesi/anni
    EMOTIONAL = "EMOTIONAL"  # eventi emotivamente forti, persiste a lungo


#: Tasso di decadimento (saliency sottratta per giorno).
DECAY_RATES: dict[MemoryKind, float] = {
    MemoryKind.SHORT_TERM: 0.20,
    MemoryKind.LONG_TERM: 0.01,
    MemoryKind.EMOTIONAL: 0.002,
}

#: Soglia sotto cui una memoria viene eliminata.
MIN_SALIENCY: float = 0.05


__all__ = ["DECAY_RATES", "MIN_SALIENCY", "MemoryKind"]
