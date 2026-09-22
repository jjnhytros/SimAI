"""Nodi foglia: Condition e ActionLeaf."""

from __future__ import annotations

from collections.abc import Callable

from simai.npc.ai.bt.base import Blackboard, BTNode
from simai.npc.ai.bt.status import BTStatus


class Condition(BTNode):
    """Valuta un predicato. SUCCESS se vero, FAILURE altrimenti."""

    def __init__(
        self,
        predicate: Callable[[Blackboard], bool],
        name: str = "",
    ) -> None:
        super().__init__(name)
        self._predicate = predicate

    def tick(self, blackboard: Blackboard) -> BTStatus:
        try:
            ok = bool(self._predicate(blackboard))
        except Exception:
            return BTStatus.FAILURE
        return BTStatus.SUCCESS if ok else BTStatus.FAILURE


class ActionLeaf(BTNode):
    """Esegue una funzione `Callable[[Blackboard], BTStatus]`."""

    def __init__(
        self,
        fn: Callable[[Blackboard], BTStatus],
        name: str = "",
    ) -> None:
        super().__init__(name)
        self._fn = fn

    def tick(self, blackboard: Blackboard) -> BTStatus:
        return self._fn(blackboard)


class AlwaysSucceed(BTNode):
    """Nodo che ritorna sempre SUCCESS. Utile come foglia neutra."""

    def tick(self, blackboard: Blackboard) -> BTStatus:
        return BTStatus.SUCCESS


class AlwaysFail(BTNode):
    """Nodo che ritorna sempre FAILURE."""

    def tick(self, blackboard: Blackboard) -> BTStatus:
        return BTStatus.FAILURE


class WaitLeaf(BTNode):
    """Attende `ticks` tick, invocando una callback ad ogni tick.

    Il contatore è interno e persiste tra tick (fino a `reset()`).
    """

    def __init__(
        self,
        ticks: int,
        on_tick: Callable[[Blackboard], None] | None = None,
        name: str = "",
    ) -> None:
        super().__init__(name)
        if ticks < 1:
            raise ValueError(f"ticks deve essere >= 1, ricevuto {ticks}")
        self._ticks = ticks
        self._remaining = ticks
        self._on_tick = on_tick

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def remaining(self) -> int:
        return self._remaining

    def tick(self, blackboard: Blackboard) -> BTStatus:
        if self._on_tick is not None:
            self._on_tick(blackboard)
        self._remaining -= 1
        if self._remaining <= 0:
            return BTStatus.SUCCESS
        return BTStatus.RUNNING

    def reset(self) -> None:
        self._remaining = self._ticks


__all__ = [
    "ActionLeaf",
    "AlwaysFail",
    "AlwaysSucceed",
    "Condition",
    "WaitLeaf",
]
