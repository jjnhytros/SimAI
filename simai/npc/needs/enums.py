"""Enum del dominio bisogni."""

from enum import StrEnum


class NeedType(StrEnum):
    """Bisogni primari e secondari di un Character.

    Ogni bisogno ha un valore in [0, 100]:
      - 100 = soddisfatto completamente
      - 0   = critico
    """

    HUNGER = "hunger"
    THIRST = "thirst"
    BLADDER = "bladder"
    ENERGY = "energy"
    HYGIENE = "hygiene"
    SOCIAL = "social"
    FUN = "fun"
    COMFORT = "comfort"
    INTIMACY = "intimacy"
    SOLITUDE = "solitude"


class NeedState(StrEnum):
    """Stato qualitativo di un bisogno."""

    CRITICAL = "CRITICAL"  # [0, 10)
    LOW = "LOW"  # [10, 30)
    OK = "OK"  # [30, 70)
    HIGH = "HIGH"  # [70, 100]


__all__ = ["NeedState", "NeedType"]
