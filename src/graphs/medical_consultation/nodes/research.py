from __future__ import annotations

from typing import Any, Callable


def run(state: dict[str, Any], services: dict[str, Any]) -> dict[str, Any]:
    retrieve_fn = services.get("retrieve_evidence")
    evidence: list[dict[str, Any]]
    if callable(retrieve_fn):
        evidence = list(_call_retriever(retrieve_fn, state))
    else:
        evidence = [
            {
                "evidence_id": "default_evidence_1",
                "source_id": "internal_guideline_1",
                "source_type": "guideline",
                "title": "General symptom triage guidance",
                "locator": "sec-1",
                "content": "Baseline conservative guidance applies.",
            }
        ]
    return {"research_evidence": evidence}


def _call_retriever(
    retrieve_fn: Callable[[dict[str, Any]], list[dict[str, Any]]], state: dict[str, Any]
) -> list[dict[str, Any]]:
    return retrieve_fn(state)
