"""Needs — contenitore dei valori dei bisogni di un Character.

Immutabile lato API pubblica (i metodi `with_*` ritornano un nuovo oggetto),
ma serializzabile da/verso `dict[str, float]` per storage JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.thresholds import (
    MAX_NEED_VALUE,
    MIN_NEED_VALUE,
    state_of,
)

#: Valore iniziale di tutti i bisogni (appena soddisfatti).
DEFAULT_NEED_VALUE: float = 80.0


@dataclass(frozen=True, slots=True)
class Needs:
    """Valori correnti dei bisogni di un Character."""

    values: dict[NeedType, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Normalizza: assicura che TUTTI i need siano presenti
        normalized: dict[NeedType, float] = {}
        for need in NeedType:
            v = self.values.get(need, DEFAULT_NEED_VALUE)
            if v < MIN_NEED_VALUE or v > MAX_NEED_VALUE:
                raise ValueError(f"Bisogno {need.value} fuori range [0, 100]: {v}")
            normalized[need] = v
        object.__setattr__(self, "values", normalized)

    # ------------------------------------------------------------------
    # Accesso
    # ------------------------------------------------------------------

    def get(self, need: NeedType) -> float:
        """Valore del bisogno `need`."""
        return self.values[need]

    def state(self, need: NeedType) -> NeedState:
        """Stato qualitativo del bisogno `need`."""
        return state_of(self.values[need])

    def states(self) -> dict[NeedType, NeedState]:
        """Stato qualitativo di tutti i bisogni."""
        return {n: state_of(v) for n, v in self.values.items()}

    def critical_needs(self) -> list[NeedType]:
        """Bisogni in stato CRITICAL."""
        return [n for n in NeedType if self.state(n) is NeedState.CRITICAL]

    def low_or_critical(self) -> list[NeedType]:
        """Bisogni in stato LOW o CRITICAL."""
        return [n for n in NeedType if self.state(n) in (NeedState.LOW, NeedState.CRITICAL)]

    # ------------------------------------------------------------------
    # Modifica
    # ------------------------------------------------------------------

    def with_delta(self, need: NeedType, delta: float) -> Needs:
        """Nuovo `Needs` con `need` variato di `delta`, clampato a [0, 100]."""
        new_values = dict(self.values)
        new_value = new_values[need] + delta
        new_values[need] = max(MIN_NEED_VALUE, min(MAX_NEED_VALUE, new_value))
        return replace(self, values=new_values)

    def with_decay(self, decay_per_tick: dict[NeedType, float]) -> Needs:
        """Nuovo `Needs` con tutti i bisogni decrementati di `decay_per_tick`."""
        new_values = dict(self.values)
        for need, rate in decay_per_tick.items():
            new_value = new_values[need] - rate
            new_values[need] = max(MIN_NEED_VALUE, min(MAX_NEED_VALUE, new_value))
        return replace(self, values=new_values)

    def with_set(self, need: NeedType, value: float) -> Needs:
        """Nuovo `Needs` con `need` impostato a `value`, clampato."""
        if value < MIN_NEED_VALUE or value > MAX_NEED_VALUE:
            value = max(MIN_NEED_VALUE, min(MAX_NEED_VALUE, value))
        new_values = dict(self.values)
        new_values[need] = value
        return replace(self, values=new_values)

    # ------------------------------------------------------------------
    # Serializzazione
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, float]:
        """Dizionario `{need_name: value}` per storage JSON."""
        return {n.value: v for n, v in self.values.items()}

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Needs:
        """Deserializza da JSON. Chiavi sconosciute vengono ignorate."""
        values: dict[NeedType, float] = {}
        for need in NeedType:
            if need.value in data:
                values[need] = float(data[need.value])
        return cls(values=values)

    @classmethod
    def default(cls) -> Needs:
        """Needs tutti a `DEFAULT_NEED_VALUE` (80.0)."""
        return cls(values=dict.fromkeys(NeedType, DEFAULT_NEED_VALUE))


__all__ = ["DEFAULT_NEED_VALUE", "Needs"]
