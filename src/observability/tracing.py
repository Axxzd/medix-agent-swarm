from __future__ import annotations

from typing import Any


PHI_KEYS = {"patient_name", "name", "phone", "email", "id_number", "address"}


def sanitize_trace_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in PHI_KEYS:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_trace_payload(value)
        return sanitized
    if isinstance(payload, list):
        return [sanitize_trace_payload(item) for item in payload]
    return payload
