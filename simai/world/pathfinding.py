"""Pathfinding A* sul grafo Location <-> LocationEdge.

Carica il grafo dal DB in memoria (una volta per query) e usa A* con
euristica euclidea sui centri delle location. Se i bounds sono degeneri,
l'euristica è 0 e A* degenera in Dijkstra (comportamento corretto).
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.world.models import Location, LocationEdge


@dataclass(frozen=True, slots=True)
class PathResult:
    """Risultato di un pathfinding: nodi attraversati + distanza totale."""

    nodes: list[int]
    total_distance: float


class LocationGraph:
    """Grafo di navigazione in memoria.

    Nodi: id Location. Archi: `LocationEdge` (con `distance` come costo).
    """

    def __init__(self) -> None:
        self._adj: dict[int, list[tuple[int, float]]] = {}
        self._centers: dict[int, tuple[float, float]] = {}

    # ------------------------------------------------------------------
    # Costruzione
    # ------------------------------------------------------------------

    def add_node(self, node_id: int, center: tuple[float, float]) -> None:
        self._adj.setdefault(node_id, [])
        self._centers[node_id] = center

    def add_edge(
        self,
        from_id: int,
        to_id: int,
        distance: float,
        *,
        bidirectional: bool = True,
        accessible: bool = True,
    ) -> None:
        if not accessible:
            return
        self._adj.setdefault(from_id, []).append((to_id, distance))
        if bidirectional:
            self._adj.setdefault(to_id, []).append((from_id, distance))

    @classmethod
    def from_session(cls, session: Session) -> LocationGraph:
        """Costruisce il grafo da DB (una SELECT per tabella)."""
        g = cls()
        for loc in session.scalars(select(Location)):
            g.add_node(loc.id, loc.center())
        for edge in session.scalars(select(LocationEdge)):
            g.add_edge(
                edge.from_location_id,
                edge.to_location_id,
                edge.distance,
                bidirectional=edge.bidirectional,
                accessible=edge.is_accessible,
            )
        return g

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def node_count(self) -> int:
        return len(self._adj)

    def edge_count(self) -> int:
        return sum(len(v) for v in self._adj.values())

    def neighbors(self, node_id: int) -> Iterable[tuple[int, float]]:
        return iter(self._adj.get(node_id, []))

    def _heuristic(self, a: int, b: int) -> float:
        ca = self._centers.get(a)
        cb = self._centers.get(b)
        if ca is None or cb is None:
            return 0.0
        dx = ca[0] - cb[0]
        dy = ca[1] - cb[1]
        return math.hypot(dx, dy)

    # ------------------------------------------------------------------
    # A*
    # ------------------------------------------------------------------

    def find_path(
        self,
        from_id: int,
        to_id: int,
        *,
        accessible_only: bool = False,
    ) -> PathResult | None:
        """A* da `from_id` a `to_id`. ``None`` se non esiste percorso.

        `accessible_only` è già filtrato in `add_edge` (edge non accessibili
        non entrano nel grafo). Il parametro è mantenuto per compatibilità
        futura con multi-grafo.
        """
        if from_id not in self._adj or to_id not in self._adj:
            return None
        if from_id == to_id:
            return PathResult(nodes=[from_id], total_distance=0.0)

        # g-score: costo effettivo dal start
        g: dict[int, float] = {from_id: 0.0}
        # f-score = g + h
        f: dict[int, float] = {from_id: self._heuristic(from_id, to_id)}
        # per ricostruire il path
        came_from: dict[int, int] = {}

        # heap di (f_score, node_id)
        open_heap: list[tuple[float, int]] = [(f[from_id], from_id)]
        closed: set[int] = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            if current == to_id:
                return self._reconstruct(came_from, current, g[current])
            closed.add(current)

            for neighbor, weight in self._adj.get(current, []):
                if neighbor in closed:
                    continue
                tentative_g = g[current] + weight
                if tentative_g < g.get(neighbor, math.inf):
                    came_from[neighbor] = current
                    g[neighbor] = tentative_g
                    f[neighbor] = tentative_g + self._heuristic(neighbor, to_id)
                    heapq.heappush(open_heap, (f[neighbor], neighbor))

        return None

    @staticmethod
    def _reconstruct(came_from: dict[int, int], current: int, total_distance: float) -> PathResult:
        nodes = [current]
        while current in came_from:
            current = came_from[current]
            nodes.append(current)
        nodes.reverse()
        return PathResult(nodes=nodes, total_distance=total_distance)
