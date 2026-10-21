from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.graphs.medical_consultation.routing import (
    route_after_consultation,
    route_after_human_review,
    route_after_safety_review,
    route_after_triage,
    route_after_triage_precheck,
)


def test_route_after_triage_precheck_emergency_short_circuit() -> None:
    node = route_after_triage_precheck(
        {
            "emergency_precheck_hit": True,
            "intent_status": "resolved",
            "intent_type": "symptom_check",
            "symptom_entities": [{"name": "chest pain"}],
        }
    )
    assert node == "final_response"


def test_route_after_triage_precheck_unresolved_intent_goes_to_clarify() -> None:
    node = route_after_triage_precheck(
        {
            "emergency_precheck_hit": False,
            "intent_status": "unresolved",
            "intent_type": "medical_info",
            "symptom_entities": [],
        }
    )
    assert node == "clarify_intent"


def test_route_after_triage_precheck_medical_info_without_symptoms() -> None:
    node = route_after_triage_precheck(
        {
            "emergency_precheck_hit": False,
            "intent_status": "resolved",
            "intent_type": "medical_info",
            "symptom_entities": [],
        }
    )
    assert node == "consultation"


def test_route_after_triage_risk_levels() -> None:
    assert route_after_triage({"risk_level": "emergency"}) == "final_response"
    assert route_after_triage({"risk_level": "high"}) == "diagnostic"
    assert route_after_triage({"risk_level": "medium"}) == "consultation"
    assert route_after_triage({"risk_level": "low"}) == "consultation"


def test_route_after_consultation_by_next_action() -> None:
    assert route_after_consultation({"next_action": "finalize"}) == "final_response"
    assert (
        route_after_consultation({"next_action": "escalate_diagnostic"}) == "diagnostic"
    )
    assert (
        route_after_consultation({"next_action": "request_clarification"})
        == "clarify_intent"
    )


def test_route_after_human_review_decision() -> None:
    assert route_after_human_review({"review_decision": "approve_continue"}) == "triage"
    assert route_after_human_review({"review_decision": "safe_close"}) == "final_response"


def test_route_after_safety_review_default_and_escalation() -> None:
    assert route_after_safety_review({"requires_human_review": True}) == "human_review"
    assert route_after_safety_review({"requires_human_review": False}) == "final_response"
