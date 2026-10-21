from __future__ import annotations

from typing import Any

from .llm_utils import call_llm

EMERGENCY_TEMPLATE = (
    "这可能属于紧急情况，请立即前往最近急诊或拨打当地急救电话。"
    "在等待救援期间保持呼吸道通畅，避免独处。"
)


def run(state: dict[str, Any], services: dict[str, Any]) -> dict[str, Any]:
    risk_level = state.get("risk_level") or "low"
    end_reason = state.get("end_reason") or "normal_finalize"
    question = str(state.get("normalized_question") or "")
    synthesized_answer = str(state.get("synthesized_answer") or "")

    if risk_level == "emergency":
        candidate = EMERGENCY_TEMPLATE
        end_reason = "emergency"
    elif end_reason == "safe_close_timeout":
        candidate = "人工审核超时。为安全起见，请尽快线下就医或联系急救服务。"
    elif end_reason == "safe_close_human":
        candidate = "人工审核建议先进行线下医疗评估。"
    else:
        candidate = (
            synthesized_answer
            or "当前信息不足以给出确定判断，建议线下就医进一步检查。"
        )

    answer = call_llm(
        services=services,
        system_prompt=(
            "You are a medical response finalizer. "
            "Use Chinese. Keep safety-first wording. "
            "Do not provide definitive diagnosis or medication dosage. "
            "Always include a brief escalation condition."
        ),
        user_prompt=(
            f"用户问题：{question}\n"
            f"风险等级：{risk_level}\n"
            f"结束原因：{end_reason}\n"
            f"候选答案：{candidate}\n"
            "请输出最终用户回答。"
        ),
    )

    return {
        "graph_status": "completed",
        "end_reason": end_reason,
        "final_response": {
            "answer": answer,
            "risk_level": risk_level,
            "end_reason": end_reason,
        },
    }
