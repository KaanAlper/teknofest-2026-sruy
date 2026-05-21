"""RouteGraph Dijkstra testleri."""

from __future__ import annotations

import pytest

from domain._shared.exceptions import RouteNotFound
from domain._shared.value_objects import Pose
from domain.navigation.aggregate import RouteGraph
from domain.navigation.value_objects import Edge, NodeType, Waypoint


def _wp(node_id: str, type_: NodeType = NodeType.WAYPOINT) -> Waypoint:
    return Waypoint(node_id=node_id, type=type_, pose=Pose(0, 0, 0))


def test_shortest_path_simple_chain():
    g = RouteGraph(name="t")
    for n in ["A", "B", "C", "D"]:
        g.add_node(_wp(n))
    g.add_edge(Edge(from_id="A", to_id="B", cost=1.0))
    g.add_edge(Edge(from_id="B", to_id="C", cost=1.0))
    g.add_edge(Edge(from_id="C", to_id="D", cost=1.0))

    path = g.shortest_path("A", "D")
    assert [w.node_id for w in path] == ["A", "B", "C", "D"]


def test_shortest_path_chooses_cheaper_route():
    g = RouteGraph(name="t")
    for n in ["A", "B", "C", "D"]:
        g.add_node(_wp(n))
    g.add_edge(Edge(from_id="A", to_id="B", cost=10.0))
    g.add_edge(Edge(from_id="B", to_id="D", cost=10.0))
    g.add_edge(Edge(from_id="A", to_id="C", cost=1.0))
    g.add_edge(Edge(from_id="C", to_id="D", cost=1.0))

    path = g.shortest_path("A", "D")
    assert [w.node_id for w in path] == ["A", "C", "D"]


def test_unknown_node_raises():
    g = RouteGraph(name="t")
    g.add_node(_wp("A"))
    with pytest.raises(RouteNotFound):
        g.shortest_path("A", "Z")


def test_disconnected_raises():
    g = RouteGraph(name="t")
    g.add_node(_wp("A"))
    g.add_node(_wp("B"))
    with pytest.raises(RouteNotFound):
        g.shortest_path("A", "B")
