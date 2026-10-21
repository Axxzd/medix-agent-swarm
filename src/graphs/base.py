from __future__ import annotations

from typing import Any, Callable

from src.state.reducers import append_items, merge_citations, merge_evidence

NodeFn = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
NextFn = Callable[[dict[str, Any]], str | None]


class GraphApp:
    def __init__(
        self,
        *,
        name: str,
        version: str,
        start_node: str,
        nodes: dict[str, NodeFn],
        edges: dict[str, NextFn],
        max_steps: int = 50,
    ) -> None:
        self.name = name
        self.version = version
        self.start_node = start_node
        self.nodes = nodes
        self.edges = edges
        self.max_steps = max_steps

    def invoke(
        self, initial_state: dict[str, Any], *, services: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        state = dict(initial_state)
        runtime_services = services or {}
        executed_nodes: list[str] = []
        current = self.start_node

        for _ in range(self.max_steps):
            if current is None:
                break
            node_fn = self.nodes.get(current)
            if node_fn is None:
                raise ValueError(f"Unknown node: {current}")

            executed_nodes.append(current)
            patch = node_fn(state, runtime_services) or {}
            state = _merge_state(state, patch)

            if current == "final_response":
                state["graph_status"] = "completed"
                break

            next_fn = self.edges.get(current)
            if next_fn is None:
                break
            current = next_fn(state)
        else:
            state["graph_status"] = "failed"
            state["error_metadata"] = {
                "error_code": "max_steps_exceeded",
                "message": f"Graph exceeded max steps: {self.max_steps}",
            }

        state["execution_trace"] = {"executed_nodes": executed_nodes}
        return state


def _merge_state(state: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = dict(state)
    append_keys = {
        "messages",
        "clarification_history",
        "audit_events",
        "trace_events",
        "safety_violations",
    }
    for key, value in patch.items():
        if key in append_keys:
            merged[key] = append_items(merged.get(key), value)
            continue
        if key == "citations":
            merged[key] = merge_citations(merged.get(key), value)
            continue
        if key == "research_evidence":
            merged[key] = merge_evidence(merged.get(key), value)
            continue
        merged[key] = value
    return merged
