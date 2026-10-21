from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.graphs.medical_consultation.graph import build_medical_consultation_graph
from src.graphs.medical_consultation.state import create_initial_state


def _mock_llm(**kwargs: Any) -> str:
    user_prompt = str(kwargs.get("user_prompt", ""))
    if "口服补液盐" in user_prompt or "拉肚子" in user_prompt or "腹泻" in user_prompt:
        return (
            "从目前描述看，优先考虑急性胃肠炎。可先补液（口服补液盐）、清淡饮食、充分休息。"
            "如需药物缓解，可考虑蒙脱石散、益生菌类；不建议自行使用抗生素。"
            "若便血、持续高热、明显脱水或持续加重，请尽快线下就医。"
        )
    if "风险等级：emergency" in user_prompt:
        return "存在急症风险，请立即前往急诊或呼叫急救。"
    return "已评估当前情况，建议保守处理并关注恶化信号，必要时及时线下就医。"


def _initial(question: str) -> dict[str, Any]:
    return create_initial_state(
        task_id="t-graph",
        thread_id="th-graph",
        user_id="u1",
        trace_id="tr-graph",
        question=question,
        graph_name="medical_consultation",
        graph_version="v1",
    )


def test_emergency_path_short_circuits_without_retrieval_or_research() -> None:
    calls = {"retrieve": 0}

    def retrieve_evidence(_: dict[str, Any]) -> list[dict[str, Any]]:
        calls["retrieve"] += 1
        return [{"evidence_id": "e1", "content": "dummy"}]

    graph = build_medical_consultation_graph()
    result = graph.invoke(
        _initial("突发胸痛、呼吸困难、意识模糊，应该怎么办？"),
        services={"retrieve_evidence": retrieve_evidence, "llm_generate": _mock_llm},
    )

    executed = result["execution_trace"]["executed_nodes"]
    assert result["end_reason"] == "emergency"
    assert "final_response" in executed
    assert "diagnostic" not in executed
    assert "research" not in executed
    assert calls["retrieve"] == 0


def test_high_risk_non_emergency_path_runs_diagnostic_and_research() -> None:
    calls = {"retrieve": 0}

    def retrieve_evidence(_: dict[str, Any]) -> list[dict[str, Any]]:
        calls["retrieve"] += 1
        return [
            {
                "evidence_id": "e2",
                "source_id": "kb_1",
                "title": "Respiratory red flags",
                "content": "Example evidence",
            }
        ]

    graph = build_medical_consultation_graph()
    result = graph.invoke(
        _initial("持续高热三天，伴明显呼吸急促，但目前意识清楚"),
        services={"retrieve_evidence": retrieve_evidence, "llm_generate": _mock_llm},
    )

    executed = result["execution_trace"]["executed_nodes"]
    assert "diagnostic" in executed
    assert "research" in executed
    assert "synthesize" in executed
    assert calls["retrieve"] == 1
    assert result["graph_status"] == "completed"


def test_gastrointestinal_case_returns_actionable_non_dosage_relief_advice() -> None:
    graph = build_medical_consultation_graph()
    result = graph.invoke(
        _initial("我吃了牛蛙后肚子疼、拉肚子，可以用什么药缓解？"),
        services={"llm_generate": _mock_llm},
    )
    executed = result["execution_trace"]["executed_nodes"]
    answer = (result.get("final_response") or {}).get("answer", "")

    assert "diagnostic" in executed
    assert "research" in executed
    assert "口服补液盐" in answer
    assert "不建议自行使用抗生素" in answer
