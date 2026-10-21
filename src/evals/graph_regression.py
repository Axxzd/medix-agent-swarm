from __future__ import annotations


def compare_route(expected_nodes: list[str], actual_nodes: list[str]) -> dict[str, object]:
    expected = list(expected_nodes)
    actual = list(actual_nodes)
    return {
        "match": expected == actual,
        "expected": expected,
        "actual": actual,
    }
