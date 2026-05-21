"""RouteGraph agregası — yarışma sahasının düğüm/kenar yapısı."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Set

from domain._shared.exceptions import RouteNotFound
from domain.navigation.value_objects import Edge, Waypoint


@dataclass
class RouteGraph:
    name: str
    nodes: Dict[str, Waypoint] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)

    def add_node(self, wp: Waypoint) -> None:
        self.nodes[wp.node_id] = wp

    def add_edge(self, edge: Edge, bidirectional: bool = True) -> None:
        self.edges.append(edge)
        if bidirectional:
            self.edges.append(Edge(from_id=edge.to_id, to_id=edge.from_id, cost=edge.cost))

    def neighbors(self, node_id: str) -> List[tuple[str, float]]:
        return [(e.to_id, e.cost) for e in self.edges if e.from_id == node_id]

    def shortest_path(self, start: str, goal: str) -> List[Waypoint]:
        """Dijkstra ile en kısa yol."""
        if start not in self.nodes or goal not in self.nodes:
            raise RouteNotFound(f"Düğüm yok: {start} veya {goal}")

        dist: Dict[str, float] = {n: float("inf") for n in self.nodes}
        prev: Dict[str, str | None] = {n: None for n in self.nodes}
        dist[start] = 0.0
        pq: list[tuple[float, str]] = [(0.0, start)]
        visited: Set[str] = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            if u == goal:
                break
            for v, cost in self.neighbors(u):
                nd = d + cost
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))

        if dist[goal] == float("inf"):
            raise RouteNotFound(f"{start} → {goal} arası yol bulunamadı")

        # geri sarma
        path_ids: List[str] = []
        cur: str | None = goal
        while cur is not None:
            path_ids.append(cur)
            cur = prev[cur]
        path_ids.reverse()
        return [self.nodes[nid] for nid in path_ids]
