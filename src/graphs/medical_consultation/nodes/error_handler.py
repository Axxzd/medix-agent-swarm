from __future__ import annotations

from typing import Any


def run(state: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    return {
        "graph_status": "failed",
        "error_metadata": {
            "error_code": "graph_runtime_error",
            "message": "Graph entered error_handler node.",
        },
        "final_response": {
            "answer": "系统当前无法完成本次分析，请稍后重试或线下就医。",
            "risk_level": "medium",
            "end_reason": "failed_runtime",
        },
    }
