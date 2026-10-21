from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    decision = state.get("review_decision") or "safe_close"
    patch: dict[str, Any] = {"review_decision": decision}
    if decision == "safe_close":
        patch["end_reason"] = "safe_close_human"
    return patch
