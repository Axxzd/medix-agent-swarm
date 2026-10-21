from __future__ import annotations

from typing import Any

from src.evals.graders import grade_eval_case


def evaluate_gate_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    graded = [grade_eval_case(case) for case in cases]
    emergency_miss_count = sum(1 for item in graded if item["emergency_miss"])
    high_severity_leakage_count = sum(1 for item in graded if item["high_severity_leakage"])
    passed = emergency_miss_count == 0 and high_severity_leakage_count == 0
    return {
        "total_cases": len(cases),
        "emergency_miss_count": emergency_miss_count,
        "high_severity_leakage_count": high_severity_leakage_count,
        "pass": passed,
    }
