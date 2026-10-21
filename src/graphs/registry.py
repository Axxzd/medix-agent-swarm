from __future__ import annotations

from src.graphs.base import GraphApp


class GraphRegistry:
    def __init__(self) -> None:
        self._graphs: dict[tuple[str, str], GraphApp] = {}

    def register(self, graph: GraphApp) -> None:
        self._graphs[(graph.name, graph.version)] = graph

    def get(self, graph_name: str, graph_version: str) -> GraphApp:
        key = (graph_name, graph_version)
        graph = self._graphs.get(key)
        if graph is None:
            raise KeyError(f"Graph not found: {graph_name}@{graph_version}")
        return graph
