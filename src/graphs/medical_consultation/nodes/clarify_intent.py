from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    rounds = int(state.get("clarification_rounds", 0)) + 1
    question = str(state.get("normalized_question") or state.get("raw_user_input") or "")
    return {
        "clarification_rounds": rounds,
        "clarification_history": [
            {
                "round_index": rounds,
                "prompt": "请补充症状出现时间、严重程度和伴随表现。",
                "user_reply": question,
            }
        ],
        "intent_status": "resolved" if question else "unresolved",
    }
