from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    question = str(state.get("raw_user_input") or "").strip()
    symptom_keywords = (
        "痛",
        "疼",
        "发烧",
        "咳",
        "呼吸",
        "头晕",
        "胸闷",
        "恶心",
        "呕吐",
        "腹",
        "肚子",
        "拉肚子",
        "腹泻",
        "腹痛",
    )
    has_symptom = any(keyword in question for keyword in symptom_keywords)

    if has_symptom:
        intent_type = "symptom_check"
        intent_status = "resolved"
    elif any(keyword in question for keyword in ("是什么", "如何", "怎么", "预防", "科普")):
        intent_type = "medical_info"
        intent_status = "resolved"
    else:
        intent_type = "unknown"
        intent_status = "unresolved"

    return {
        "normalized_question": question,
        "intent_type": intent_type,
        "intent_status": intent_status,
    }
