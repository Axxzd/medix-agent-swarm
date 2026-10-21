from __future__ import annotations

from typing import Any

from .llm_utils import call_llm


def run(state: dict[str, Any], services: dict[str, Any]) -> dict[str, Any]:
    if state.get("intent_status") != "resolved":
        return {"next_action": "request_clarification"}

    question = str(state.get("normalized_question") or "")
    risk_level = state.get("risk_level")
    if any(keyword in question for keyword in ("用药", "吃什么药", "药物", "缓解")):
        return {"next_action": "escalate_diagnostic"}

    if risk_level == "medium":
        return {"next_action": "escalate_diagnostic"}

    advice = call_llm(
        services=services,
        system_prompt=(
            "You are a cautious medical assistant. "
            "Give practical, non-diagnostic, non-dosage guidance. "
            "Use concise Chinese. Always include warning signs for escalation."
        ),
        user_prompt=(
            f"用户问题：{question}\n"
            f"风险等级：{risk_level}\n"
            "请给出：\n"
            "1) 当前最可能的非紧急解释（非确诊）\n"
            "2) 可执行的居家处理建议\n"
            "3) 何时必须线下就医或急诊"
        ),
    )

    return {
        "next_action": "finalize",
        "synthesized_answer": advice,
    }
