"""NeedsProcessor — aggiorna i bisogni di un Character ad ogni tick."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from simai.npc.needs.enums import NeedState, NeedType
from simai.npc.needs.needs import Needs

# ---------------------------------------------------------------------------
# Tassi di decadimento per tick (default, in punti bisogno/tick)
# ---------------------------------------------------------------------------
#
# 1 giorno Anthalys = 336 tick (28h * 60min / 5min).
# Rate target: "svuotare" il bisogno in N ore di veglia.
#
#   hunger  : ~18h -> 0.40/tick
#   thirst  : ~10h -> 0.70/tick
#   bladder : ~12h -> 0.60/tick
#   energy  : ~16h -> 0.40/tick
#   hygiene : ~40h -> 0.17/tick
#   social  : ~46h -> 0.15/tick
#   fun     : ~23h -> 0.30/tick
#   comfort : ~70h -> 0.10/tick

DEFAULT_DECAY_RATES: Final[dict[NeedType, float]] = {
    NeedType.HUNGER: 0.40,
    NeedType.THIRST: 0.70,
    NeedType.BLADDER: 0.60,
    NeedType.ENERGY: 0.40,
    NeedType.HYGIENE: 0.17,
    NeedType.SOCIAL: 0.15,
    NeedType.FUN: 0.30,
    NeedType.COMFORT: 0.10,
    NeedType.INTIMACY: 0.08,  # ~4-5 giorni per svuotarsi
    NeedType.SOLITUDE: 0.06,  # ~6 giorni per svuotarsi
}


@dataclass(frozen=True, slots=True)
class NeedTransition:
    """Transizione di stato di un bisogno rilevata al tick."""

    need: NeedType
    from_state: NeedState
    to_state: NeedState


class NeedsProcessor:
    """Applica decadimento ai bisogni e rileva transizioni di stato.

    Non è un singleton. Un'istanza può essere condivisa (stateless).
    """

    def __init__(
        self,
        decay_rates: dict[NeedType, float] | None = None,
    ) -> None:
        rates = decay_rates if decay_rates is not None else DEFAULT_DECAY_RATES
        for need, rate in rates.items():
            if rate < 0:
                raise ValueError(f"Rate di decadimento negativo per {need.value}: {rate}")
        self._rates = dict(rates)

    @property
    def rates(self) -> dict[NeedType, float]:
        return dict(self._rates)

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self, needs: Needs) -> tuple[Needs, list[NeedTransition]]:
        """Applica un tick di decadimento.

        Ritorna `(nuovo_needs, transizioni)`.
        """
        before_states = {n: needs.state(n) for n in NeedType}
        new_needs = needs.with_decay(self._rates)
        transitions: list[NeedTransition] = []
        for n in NeedType:
            before = before_states[n]
            after = new_needs.state(n)
            if before is not after:
                transitions.append(NeedTransition(need=n, from_state=before, to_state=after))
        return new_needs, transitions


__all__ = ["DEFAULT_DECAY_RATES", "NeedTransition", "NeedsProcessor"]
