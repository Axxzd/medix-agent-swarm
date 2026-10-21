from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    if state.get("emergency_precheck_hit"):
        return {"risk_level": "emergency", "end_reason": "emergency"}

    question = str(state.get("normalized_question") or "")
    high_risk_keywords = (
        "高热",
        "持续高烧",
        "呼吸急促",
        "剧烈",
        "持续加重",
        "便血",
        "黑便",
        "脱水",
        "尿少",
        "无法进食",
        "无法喝水",
    )
    medium_risk_keywords = (
        "发烧",
        "疼痛",
        "肚子疼",
        "腹痛",
        "腹泻",
        "拉肚子",
        "恶心",
        "呕吐",
        "咳嗽",
        "头痛",
    )

    if any(keyword in question for keyword in high_risk_keywords):
        return {"risk_level": "high"}
    if any(keyword in question for keyword in medium_risk_keywords):
        return {"risk_level": "medium"}
    return {"risk_level": "low"}
