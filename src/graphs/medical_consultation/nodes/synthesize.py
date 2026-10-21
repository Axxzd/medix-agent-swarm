from __future__ import annotations

from typing import Any

from .llm_utils import call_llm


def run(state: dict[str, Any], services: dict[str, Any]) -> dict[str, Any]:
    differential = (
        state.get("diagnostic_result", {}).get("differential", [])
        if isinstance(state.get("diagnostic_result"), dict)
        else []
    )
    question = str(state.get("normalized_question") or "")
    top = differential[0] if differential else "需进一步评估"
    evidence_count = len(state.get("research_evidence") or [])

    answer = call_llm(
        services=services,
        system_prompt=(
            "You are a conservative medical synthesis assistant. "
            "Never give definitive diagnosis or dosage. "
            "Return concise Chinese guidance with clear escalation conditions."
        ),
        user_prompt=(
            f"用户问题：{question}\n"
            f"鉴别分析首位：{top}\n"
            f"证据条数：{evidence_count}\n"
            f"全部鉴别列表：{differential}\n"
            "请输出最终候选回答：包括可能解释、处理建议、风险升级条件。"
        ),
    )
    return {"synthesized_answer": answer}
