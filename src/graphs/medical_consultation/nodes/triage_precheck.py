from __future__ import annotations

from typing import Any


EMERGENCY_KEYWORDS = (
    "胸痛",
    "呼吸困难",
    "意识模糊",
    "昏迷",
    "抽搐",
    "大出血",
    "中风",
    "自杀",
    "无法呼吸",
)


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    question = str(state.get("normalized_question") or state.get("raw_user_input") or "")
    hit = any(keyword in question for keyword in EMERGENCY_KEYWORDS)
    patch: dict[str, Any] = {"emergency_precheck_hit": hit}
    if hit:
        patch["risk_level"] = "emergency"
        patch["end_reason"] = "emergency"
    return patch
