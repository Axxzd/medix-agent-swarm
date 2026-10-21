from __future__ import annotations

from typing import Any


def build_langsmith_trace_payload(
    *, enabled: bool, run_name: str, metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    if not enabled:
        return {"enabled": False}
    return {
        "enabled": True,
        "run_name": run_name,
        "metadata": metadata or {},
    }
