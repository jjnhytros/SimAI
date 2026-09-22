"""A* pathfinding su RoadTile."""

from __future__ import annotations

import heapq
import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.city.infrastructure.models import RoadTile

#: Penalità per condition degradata (0.0 = 1x costo, 1.0 = 3x costo).
_CONDITION_PENALTY_WEIGHT: Final[float] = 2.0


@dataclass(frozen=True, slots=True)
class RoadPath:
    """Percorso su strada (lista di celle + costo totale)."""

    cells: tuple[tuple[int, int], ...]
    total_cost: float

    @property
    def length(self) -> int:
        return len(self.cells)

    @property
    def euclidean_distance(self) -> float:
        if len(self.cells) < 2:
            return 0.0
        dx = self.cells[-1][0] - self.cells[0][0]
        dy = self.cells[-1][1] - self.cells[0][1]
        return math.hypot(dx, dy)


class RoadGraph:
    """Grafo in-memory di RoadTile (4-direzionale)."""

    def __init__(self) -> None:
        self._nodes: dict[tuple[int, int], float] = {}
        self._centers: dict[tuple[int, int], float] = {}

    @classmethod
    def from_session(cls, session: Session) -> RoadGraph:
        """Costruisce il grafo da DB (una SELECT)."""
        g = cls()
        for road in session.scalars(select(RoadTile)):
            g._nodes[(road.x, road.y)] = road.condition
        return g

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def node_count(self) -> int:
        return len(self._nodes)

    def has_node(self, x: int, y: int) -> bool:
        return (x, y) in self._nodes

    def nearest_node(self, x: int, y: int) -> tuple[int, int] | None:
        """Nodo più vicino in distanza Manhattan."""
        if not self._nodes:
            return None
        best: tuple[int, int] | None = None
        best_dist = 10**9
        for node in self._nodes:
            d = abs(node[0] - x) + abs(node[1] - y)
            if d < best_dist:
                best_dist = d
                best = node
        return best

    # ------------------------------------------------------------------
    # A*
    # ------------------------------------------------------------------

    def _neighbors(self, node: tuple[int, int]) -> Iterable[tuple[tuple[int, int], float]]:
        x, y = node
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (x + dx, y + dy)
            condition = self._nodes.get(neighbor)
            if condition is None:
                continue
            cost = 1.0 + (1.0 - condition) * _CONDITION_PENALTY_WEIGHT
            yield neighbor, cost

    def find_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> RoadPath | None:
        """A* da `start` a `goal` (4-direzionale, euristica Manhattan)."""
        if start not in self._nodes or goal not in self._nodes:
            return None
        if start == goal:
            return RoadPath(cells=(start,), total_cost=0.0)

        open_heap: list[tuple[float, tuple[int, int]]] = []
        heapq.heappush(open_heap, (0.0, start))
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_score: dict[tuple[int, int], float] = {start: 0.0}
        closed: set[tuple[int, int]] = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current == goal:
                path: list[tuple[int, int]] = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return RoadPath(
                    cells=tuple(path),
                    total_cost=g_score[goal],
                )
            if current in closed:
                continue
            closed.add(current)
            for neighbor, cost in self._neighbors(current):
                if neighbor in closed:
                    continue
                tentative = g_score[current] + cost
                if tentative < g_score.get(neighbor, math.inf):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    h = abs(neighbor[0] - goal[0]) + abs(neighbor[1] - goal[1])
                    heapq.heappush(open_heap, (tentative + h, neighbor))
        return None


__all__ = ["RoadGraph", "RoadPath"]
