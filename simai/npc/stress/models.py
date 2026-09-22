"""Modelli del dominio stress."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StressFactors:
    """Fattori che contribuiscono allo stress. Ognuno in [0, 1]."""

    critical_needs_fraction: float = 0.0
    low_mood: float = 0.0
    high_inhibition: float = 0.0
    recent_rejection: float = 0.0
    poverty: float = 0.0
    fatigue: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "critical_needs_fraction",
            "low_mood",
            "high_inhibition",
            "recent_rejection",
            "poverty",
            "fatigue",
        ):
            v = getattr(self, name)
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{name} deve essere in [0, 1], ricevuto {v}")


__all__ = ["StressFactors"]
