from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    question = str(state.get("normalized_question") or "")
    differential: list[str]
    if "呼吸" in question:
        differential = ["呼吸道感染", "肺部炎症", "哮喘急性发作"]
    elif any(keyword in question for keyword in ("拉肚子", "腹泻", "腹痛", "肚子疼", "恶心", "呕吐")):
        differential = ["急性胃肠炎", "食物不耐受/食物刺激", "肠道感染"]
    elif "腹" in question:
        differential = ["急性胃肠炎", "消化道痉挛", "腹部炎症"]
    else:
        differential = ["非特异性症状，需要线下评估"]

    return {
        "diagnostic_result": {
            "differential": differential,
            "confidence": 0.62,
            "rationale": "基于症状关键词进行非确诊性鉴别。",
        }
    }
