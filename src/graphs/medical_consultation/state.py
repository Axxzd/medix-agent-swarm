from __future__ import annotations

from typing import Annotated, Any, Literal, TypedDict

from src.state.reducers import append_items, merge_citations, merge_evidence


class ClarificationTurn(TypedDict):
    round_index: int
    prompt: str
    user_reply: str


class SymptomEntity(TypedDict):
    name: str
    severity: str
    duration: str | None


class DiagnosticResult(TypedDict):
    differential: list[str]
    confidence: float
    rationale: str


class EvidenceItem(TypedDict, total=False):
    evidence_id: str
    source_id: str
    source_type: str
    title: str
    locator: str
    content: str
    url: str
    evidence_quality: str


class SafetyViolation(TypedDict):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    message: str


class AuditEvent(TypedDict):
    event_type: str
    node_name: str
    detail: dict[str, Any]


class MedicalGraphState(TypedDict):
    user_id: str
    task_id: str
    thread_id: str
    trace_id: str
    graph_name: str
    graph_version: str

    raw_user_input: str
    normalized_question: str

    intent_type: str
    intent_confidence: float
    intent_status: Literal["resolved", "ambiguous", "unresolved"]
    missing_required_slots: list[str]

    clarification_rounds: int
    clarification_history: Annotated[list[dict[str, Any]], append_items]

    symptom_entities: list[SymptomEntity]
    emergency_precheck_hit: bool
    risk_level: Literal["low", "medium", "high", "emergency"]

    next_action: str
    graph_status: Literal["running", "interrupted", "completed", "failed", "cancelled"]
    end_reason: str | None

    diagnostic_result: DiagnosticResult | None
    research_evidence: Annotated[list[dict[str, Any]], merge_evidence]
    synthesized_answer: str | None

    citations: Annotated[list[dict[str, Any]], merge_citations]
    safety_violations: Annotated[list[dict[str, Any]], append_items]
    audit_events: Annotated[list[dict[str, Any]], append_items]
    trace_events: Annotated[list[dict[str, Any]], append_items]
    messages: Annotated[list[dict[str, Any]], append_items]

    review_decision: str | None
    final_response: dict[str, Any] | None
    error_metadata: dict[str, Any] | None


def create_initial_state(
    *,
    task_id: str,
    thread_id: str,
    user_id: str,
    trace_id: str,
    question: str,
    graph_name: str,
    graph_version: str,
) -> MedicalGraphState:
    return MedicalGraphState(
        user_id=user_id,
        task_id=task_id,
        thread_id=thread_id,
        trace_id=trace_id,
        graph_name=graph_name,
        graph_version=graph_version,
        raw_user_input=question,
        normalized_question=question.strip(),
        intent_type="unknown",
        intent_confidence=0.0,
        intent_status="unresolved",
        missing_required_slots=[],
        clarification_rounds=0,
        clarification_history=[],
        symptom_entities=[],
        emergency_precheck_hit=False,
        risk_level="low",
        next_action="continue",
        graph_status="running",
        end_reason=None,
        diagnostic_result=None,
        research_evidence=[],
        synthesized_answer=None,
        citations=[],
        safety_violations=[],
        audit_events=[],
        trace_events=[],
        messages=[],
        review_decision=None,
        final_response=None,
        error_metadata=None,
    )
