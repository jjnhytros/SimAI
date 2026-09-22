"""Nodi base del Behaviour Tree."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from simai.npc.ai.bt.status import BTStatus


class Blackboard:
    """Stato condiviso tra i nodi del BT durante un tick."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def has(self, key: str) -> bool:
        return key in self._data

    def clear(self) -> None:
        self._data.clear()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class BTNode(ABC):
    """Nodo astratto del Behaviour Tree."""

    def __init__(self, name: str = "") -> None:
        self.name = name or self.__class__.__name__

    @abstractmethod
    def tick(self, blackboard: Blackboard) -> BTStatus:
        """Esegue un tick. Ritorna lo stato."""

    def reset(self) -> None:
        """Resetta lo stato interno (default: no-op).

        I nodi che mantengono stato (WaitLeaf, Repeat, Cooldown) fanno
        override; i nodi stateless usano questo default.
        """
        return

    def child_nodes(self) -> list[BTNode]:
        """Ritorna i figli (default: nessuno). Override nei compositi/decoratori."""
        return []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


__all__ = ["BTNode", "Blackboard"]
