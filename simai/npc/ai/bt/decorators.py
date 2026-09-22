"""Nodi decoratori: Inverter, Succeeder, Repeat, Cooldown."""

from __future__ import annotations

from simai.npc.ai.bt.base import Blackboard, BTNode
from simai.npc.ai.bt.status import BTStatus


class Inverter(BTNode):
    """Inverte SUCCESS ↔ FAILURE. RUNNING passa invariato."""

    def __init__(self, child: BTNode, name: str = "") -> None:
        super().__init__(name)
        self._child = child

    def tick(self, blackboard: Blackboard) -> BTStatus:
        s = self._child.tick(blackboard)
        if s is BTStatus.SUCCESS:
            return BTStatus.FAILURE
        if s is BTStatus.FAILURE:
            return BTStatus.SUCCESS
        return BTStatus.RUNNING

    def reset(self) -> None:
        self._child.reset()


class Succeeder(BTNode):
    """Trasforma qualunque esito non-RUNNING in SUCCESS."""

    def __init__(self, child: BTNode, name: str = "") -> None:
        super().__init__(name)
        self._child = child

    def tick(self, blackboard: Blackboard) -> BTStatus:
        s = self._child.tick(blackboard)
        if s is BTStatus.RUNNING:
            return BTStatus.RUNNING
        return BTStatus.SUCCESS

    def reset(self) -> None:
        self._child.reset()


class Repeat(BTNode):
    """Ripete il figlio fino a `times` SUCCESS (o infinito se `times=0`)."""

    def __init__(self, child: BTNode, times: int = 0, name: str = "") -> None:
        super().__init__(name)
        if times < 0:
            raise ValueError(f"times deve essere >= 0, ricevuto {times}")
        self._child = child
        self._times = times
        self._count = 0

    def tick(self, blackboard: Blackboard) -> BTStatus:
        status = self._child.tick(blackboard)
        if status is BTStatus.RUNNING:
            return BTStatus.RUNNING
        if status is BTStatus.SUCCESS:
            self._count += 1
            if self._times > 0 and self._count >= self._times:
                return BTStatus.SUCCESS
            self._child.reset()
            return BTStatus.RUNNING
        return BTStatus.FAILURE

    def reset(self) -> None:
        self._child.reset()
        self._count = 0


class Cooldown(BTNode):
    """Esegue il figlio solo se sono passati almeno `cooldown_ticks`.

    Usa una chiave sul blackboard per memorizzare l'ultimo tick di esecuzione.
    """

    def __init__(
        self,
        child: BTNode,
        cooldown_ticks: int,
        *,
        key: str = "current_tick",
        name: str = "",
    ) -> None:
        super().__init__(name)
        if cooldown_ticks < 0:
            raise ValueError(f"cooldown_ticks deve essere >= 0, ricevuto {cooldown_ticks}")
        self._child = child
        self._cooldown = cooldown_ticks
        self._key = key
        self._last_tick: int = -(10**9)

    def tick(self, blackboard: Blackboard) -> BTStatus:
        current = blackboard.get(self._key, 0)
        if current - self._last_tick < self._cooldown:
            return BTStatus.FAILURE
        s = self._child.tick(blackboard)
        if s is BTStatus.SUCCESS:
            self._last_tick = current
        return s

    def reset(self) -> None:
        self._child.reset()
        self._last_tick = -(10**9)


__all__ = ["Cooldown", "Inverter", "Repeat", "Succeeder"]
