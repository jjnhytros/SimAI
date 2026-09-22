"""Modelli del dominio desiderio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DesireState:
    """Stato del desiderio.

    - `baseline`: [0.1, 0.9] tratto-like (derivato da sexuality).
    - `current`: [0, 1] valore corrente (refresh giornaliero).
    - `last_satisfied_at`: timestamp ultimo soddisfacimento (total_seconds).
    """

    baseline: float = 0.5
    current: float = 0.5
    last_satisfied_at: int = 0

    def __post_init__(self) -> None:
        if not (0.0 <= self.baseline <= 1.0):
            raise ValueError(f"baseline in [0, 1], ricevuto {self.baseline}")
        if not (0.0 <= self.current <= 1.0):
            raise ValueError(f"current in [0, 1], ricevuto {self.current}")
        if self.last_satisfied_at < 0:
            raise ValueError(f"last_satisfied_at >= 0, ricevuto {self.last_satisfied_at}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline": self.baseline,
            "current": self.current,
            "last_satisfied_at": self.last_satisfied_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DesireState:
        if not data:
            return cls()
        return cls(
            baseline=float(data.get("baseline", 0.5)),
            current=float(data.get("current", 0.5)),
            last_satisfied_at=int(data.get("last_satisfied_at", 0)),
        )


__all__ = ["DesireState"]
