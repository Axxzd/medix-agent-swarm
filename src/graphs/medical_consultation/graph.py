from __future__ import annotations

from typing import Any

from src.graphs.base import GraphApp
from src.graphs.medical_consultation.nodes import (
    clarify_intent_node,
    consultation_node,
    diagnostic_node,
    final_response_node,
    human_review_node,
    intake_node,
    research_node,
    safety_review_node,
    synthesize_node,
    triage_node,
    triage_precheck_node,
)
from src.graphs.medical_consultation.routing import (
    route_after_consultation,
    route_after_human_review,
    route_after_safety_review,
    route_after_triage,
    route_after_triage_precheck,
)


def build_medical_consultation_graph(
    *, graph_version: str = "v1", max_clarification_rounds: int = 3
) -> GraphApp:
    nodes = {
        "intake": intake_node,
        "triage_precheck": triage_precheck_node,
        "clarify_intent": clarify_intent_node,
        "triage": triage_node,
        "consultation": consultation_node,
        "diagnostic": diagnostic_node,
        "research": research_node,
        "synthesize": synthesize_node,
        "safety_review": safety_review_node,
        "human_review": human_review_node,
        "final_response": final_response_node,
    }
    edges = {
        "intake": lambda _s: "triage_precheck",
        "triage_precheck": route_after_triage_precheck,
        "clarify_intent": lambda s: _route_after_clarify(
            s, max_clarification_rounds=max_clarification_rounds
        ),
        "triage": route_after_triage,
        "consultation": route_after_consultation,
        "diagnostic": lambda _s: "research",
        "research": lambda _s: "synthesize",
        "synthesize": lambda _s: "safety_review",
        "safety_review": route_after_safety_review,
        "human_review": route_after_human_review,
        "final_response": lambda _s: None,
    }
    return GraphApp(
        name="medical_consultation",
        version=graph_version,
        start_node="intake",
        nodes=nodes,
        edges=edges,
    )


def _route_after_clarify(
    state: dict[str, Any], *, max_clarification_rounds: int
) -> str:
    if state.get("intent_status") == "resolved":
        return "triage_precheck"
    if int(state.get("clarification_rounds", 0)) >= max_clarification_rounds:
        return "human_review"
    return "clarify_intent"
