from __future__ import annotations

from datetime import datetime
from typing import Any


def build_audit_event(
    *,
    rule_id: str,
    severity: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_type": "guardrail_violation",
        "rule_id": rule_id,
        "severity": severity,
        "message": message,
        "details": details or {},
        "created_at": datetime.utcnow().isoformat(),
    }
