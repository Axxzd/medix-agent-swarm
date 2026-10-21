from __future__ import annotations

from typing import Any


HIGH_CARDINALITY_KEYS = {"task_id", "thread_id", "user_id", "trace_id"}


def validate_metric_labels(labels: dict[str, Any]) -> dict[str, Any]:
    blocked = [key for key in labels if key in HIGH_CARDINALITY_KEYS]
    return {
        "valid": len(blocked) == 0,
        "blocked_keys": blocked,
    }
