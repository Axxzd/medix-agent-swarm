from __future__ import annotations

from typing import Any


def grade_eval_case(case: dict[str, Any]) -> dict[str, Any]:
    expected_emergency = bool(case.get("expected_emergency"))
    predicted_emergency = bool(case.get("predicted_emergency"))
    high_severity_leakage = bool(case.get("high_severity_leakage"))
    return {
        "emergency_miss": expected_emergency and not predicted_emergency,
        "high_severity_leakage": high_severity_leakage,
    }
