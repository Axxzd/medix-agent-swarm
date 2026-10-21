from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.graphs.medical_consultation.state import create_initial_state
from src.state.reducers import append_items, merge_citations, merge_evidence


def test_append_items_appends_in_order() -> None:
    current = [{"id": "1"}]
    incoming = [{"id": "2"}]
    merged = append_items(current, incoming)
    assert merged == [{"id": "1"}, {"id": "2"}]


def test_merge_citations_deduplicates_by_source_locator() -> None:
    current = [{"source_id": "s1", "locator": "A", "excerpt": "x"}]
    incoming = [
        {"source_id": "s1", "locator": "A", "excerpt": "x-new"},
        {"source_id": "s2", "locator": "B", "excerpt": "y"},
    ]
    merged = merge_citations(current, incoming)
    assert len(merged) == 2
    assert merged[0]["source_id"] == "s1"
    assert merged[1]["source_id"] == "s2"


def test_merge_evidence_deduplicates_by_evidence_id_or_hash() -> None:
    current = [{"evidence_id": "e1", "content": "A"}]
    incoming = [
        {"evidence_id": "e1", "content": "A-dup"},
        {"content": "B", "source": "kb"},
        {"content": "B", "source": "kb"},
    ]
    merged = merge_evidence(current, incoming)
    assert len(merged) == 2


def test_create_initial_state_sets_contract_defaults() -> None:
    state = create_initial_state(
        task_id="t1",
        thread_id="th1",
        user_id="u1",
        trace_id="tr1",
        question="hello",
        graph_name="medical_consultation",
        graph_version="v1",
    )
    assert state["clarification_rounds"] == 0
    assert state["graph_status"] == "running"
    assert state["citations"] == []
    assert state["audit_events"] == []
