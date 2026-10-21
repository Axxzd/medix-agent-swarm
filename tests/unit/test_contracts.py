from datetime import datetime
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contracts.outputs import Citation, InternalFinalResponse
from src.contracts.tasks import EndReason, TaskRecord, TaskStatus


def test_citation_excerpt_length_is_limited() -> None:
    with pytest.raises(ValidationError):
        Citation(
            source_id="s1",
            source_type="guideline",
            title="t",
            locator="sec-1",
            excerpt="x" * 301,
            retrieved_at=datetime.utcnow(),
            confidence=0.9,
        )


def test_citation_published_date_is_optional() -> None:
    citation = Citation(
        source_id="s1",
        source_type="guideline",
        title="t",
        locator="sec-1",
        excerpt="ok",
        retrieved_at=datetime.utcnow(),
        confidence=0.9,
    )
    assert citation.published_date is None


def test_task_status_enum_is_enforced() -> None:
    with pytest.raises(ValidationError):
        TaskRecord(
            task_id="t1",
            thread_id="th1",
            user_id="u1",
            graph_name="medical_consultation",
            graph_version="v1",
            status="bad_status",
            end_reason=None,
            payload_hash="h",
        )


def test_end_reason_enum_is_enforced() -> None:
    with pytest.raises(ValidationError):
        TaskRecord(
            task_id="t1",
            thread_id="th1",
            user_id="u1",
            graph_name="medical_consultation",
            graph_version="v1",
            status=TaskStatus.completed,
            end_reason="bad_reason",
            payload_hash="h",
        )
