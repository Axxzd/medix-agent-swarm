from __future__ import annotations

from datetime import datetime
from typing import Any

from src.observability.tracing import sanitize_trace_payload


def build_audit_record(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "payload": sanitize_trace_payload(payload),
        "created_at": datetime.utcnow().isoformat(),
    }
