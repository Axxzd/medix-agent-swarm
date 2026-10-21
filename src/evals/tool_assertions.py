from __future__ import annotations


def assert_emergency_path_constraints(executed_nodes: list[str]) -> dict[str, object]:
    blocked = {"diagnostic", "research"}
    violated = [node for node in executed_nodes if node in blocked]
    return {
        "valid": len(violated) == 0,
        "violations": violated,
    }
