from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.observability.metrics import validate_metric_labels
from src.observability.tracing import sanitize_trace_payload


def test_trace_payload_redacts_phi_fields() -> None:
    payload = {
        "patient_name": "Alice",
        "phone": "13800000000",
        "symptom": "发热",
        "nested": {"email": "alice@example.com"},
    }
    sanitized = sanitize_trace_payload(payload)
    assert sanitized["patient_name"] == "[REDACTED]"
    assert sanitized["phone"] == "[REDACTED]"
    assert sanitized["nested"]["email"] == "[REDACTED]"
    assert sanitized["symptom"] == "发热"


def test_metric_labels_block_high_cardinality_keys() -> None:
    result = validate_metric_labels(
        {
            "graph_name": "medical_consultation",
            "task_id": "task_123",
            "user_id": "u_999",
        }
    )
    assert result["valid"] is False
    assert set(result["blocked_keys"]) == {"task_id", "user_id"}
