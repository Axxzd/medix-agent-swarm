from __future__ import annotations

from typing import Any, Mapping


def route_after_triage_precheck(state: Mapping[str, Any]) -> str:
    if bool(state.get("emergency_precheck_hit")):
        return "final_response"

    if state.get("intent_status") != "resolved":
        return "clarify_intent"

    intent_type = str(state.get("intent_type", ""))
    symptom_entities = state.get("symptom_entities") or []
    if intent_type == "medical_info" and not symptom_entities:
        return "consultation"
    return "triage"


def route_after_triage(state: Mapping[str, Any]) -> str:
    risk_level = state.get("risk_level")
    if risk_level == "emergency":
        return "final_response"
    if risk_level == "high":
        return "diagnostic"
    if risk_level in {"low", "medium"}:
        return "consultation"
    raise ValueError(f"Unsupported risk_level for triage routing: {risk_level!r}")


def route_after_consultation(state: Mapping[str, Any]) -> str:
    next_action = state.get("next_action")
    if next_action == "finalize":
        return "final_response"
    if next_action == "escalate_diagnostic":
        return "diagnostic"
    if next_action == "request_clarification":
        return "clarify_intent"
    raise ValueError(f"Unsupported next_action for consultation routing: {next_action!r}")


def route_after_safety_review(state: Mapping[str, Any]) -> str:
    if bool(state.get("requires_human_review")):
        return "human_review"
    return "final_response"


def route_after_human_review(state: Mapping[str, Any]) -> str:
    decision = state.get("review_decision")
    if decision == "approve_continue":
        return "triage"
    if decision == "safe_close":
        return "final_response"
    raise ValueError(f"Unsupported review_decision for human review routing: {decision!r}")
