from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evals.runner import evaluate_gate_summary


def test_eval_gates_pass_when_no_emergency_miss_and_no_high_severity_leakage() -> None:
    summary = evaluate_gate_summary(
        [
            {"expected_emergency": True, "predicted_emergency": True, "high_severity_leakage": False},
            {"expected_emergency": False, "predicted_emergency": False, "high_severity_leakage": False},
        ]
    )
    assert summary["emergency_miss_count"] == 0
    assert summary["high_severity_leakage_count"] == 0
    assert summary["pass"] is True


def test_eval_gates_fail_on_emergency_miss() -> None:
    summary = evaluate_gate_summary(
        [
            {"expected_emergency": True, "predicted_emergency": False, "high_severity_leakage": False},
        ]
    )
    assert summary["emergency_miss_count"] == 1
    assert summary["pass"] is False


def test_eval_gates_fail_on_high_severity_leakage() -> None:
    summary = evaluate_gate_summary(
        [
            {"expected_emergency": False, "predicted_emergency": False, "high_severity_leakage": True},
        ]
    )
    assert summary["high_severity_leakage_count"] == 1
    assert summary["pass"] is False
