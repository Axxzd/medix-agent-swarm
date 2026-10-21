from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    violations = list(state.get("safety_violations") or [])
    requires_human_review = any(v.get("severity") == "high" for v in violations)
    return {"requires_human_review": requires_human_review}
