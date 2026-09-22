"""Nodi compositi: Sequence, Selector, Parallel."""

from __future__ import annotations

from simai.npc.ai.bt.base import Blackboard, BTNode
from simai.npc.ai.bt.status import BTStatus


class Sequence(BTNode):
    """Esegue i figli in ordine. Ritorna al primo FAILURE o RUNNING.

    Se tutti SUCCESS → SUCCESS.
    """

    def __init__(self, *children: BTNode, name: str = "") -> None:
        super().__init__(name)
        if not children:
            raise ValueError("Sequence richiede almeno un figlio")
        self._children = list(children)

    @property
    def children(self) -> list[BTNode]:
        return list(self._children)

    def child_nodes(self) -> list[BTNode]:
        return list(self._children)

    def tick(self, blackboard: Blackboard) -> BTStatus:
        for child in self._children:
            status = child.tick(blackboard)
            if status is not BTStatus.SUCCESS:
                return status
        return BTStatus.SUCCESS

    def reset(self) -> None:
        for c in self._children:
            c.reset()


class Selector(BTNode):
    """Esegue i figli in ordine. Ritorna al primo SUCCESS o RUNNING.

    Se tutti FAILURE → FAILURE.
    """

    def __init__(self, *children: BTNode, name: str = "") -> None:
        super().__init__(name)
        if not children:
            raise ValueError("Selector richiede almeno un figlio")
        self._children = list(children)

    @property
    def children(self) -> list[BTNode]:
        return list(self._children)

    def child_nodes(self) -> list[BTNode]:
        return list(self._children)

    def tick(self, blackboard: Blackboard) -> BTStatus:
        for child in self._children:
            status = child.tick(blackboard)
            if status is not BTStatus.FAILURE:
                return status
        return BTStatus.FAILURE

    def reset(self) -> None:
        for c in self._children:
            c.reset()


class Parallel(BTNode):
    """Esegue tutti i figli in un tick. Ritorna SUCCESS se tutti SUCCESS."""

    def __init__(
        self,
        *children: BTNode,
        require_all: bool = True,
        name: str = "",
    ) -> None:
        super().__init__(name)
        if not children:
            raise ValueError("Parallel richiede almeno un figlio")
        self._children = list(children)
        self._require_all = require_all

    @property
    def children(self) -> list[BTNode]:
        return list(self._children)

    def child_nodes(self) -> list[BTNode]:
        return list(self._children)

    def tick(self, blackboard: Blackboard) -> BTStatus:
        statuses = [c.tick(blackboard) for c in self._children]
        successes = statuses.count(BTStatus.SUCCESS)
        running = statuses.count(BTStatus.RUNNING)

        if running > 0:
            return BTStatus.RUNNING
        if self._require_all:
            return BTStatus.SUCCESS if successes == len(statuses) else BTStatus.FAILURE
        return BTStatus.SUCCESS if successes > 0 else BTStatus.FAILURE

    def reset(self) -> None:
        for c in self._children:
            c.reset()


__all__ = ["Parallel", "Selector", "Sequence"]
