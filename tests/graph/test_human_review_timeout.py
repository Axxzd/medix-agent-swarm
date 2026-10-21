from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contracts.approvals import ReviewDecision, ReviewTicketStatus
from src.contracts.tasks import EndReason, TaskRecord, TaskStatus
from src.human_in_the_loop.approvals import force_reopen_task
from src.human_in_the_loop.resume import HumanReviewWatchdog, LateResumeRejected, ResumeCoordinator
from src.human_in_the_loop.review_queue import InMemoryReviewQueue
from src.persistence.checkpointers import InProcessCheckpointer
from src.persistence.stores import SqliteRuntimeStore


def _task(
    task_id: str,
    thread_id: str,
    status: TaskStatus = TaskStatus.interrupted,
    end_reason: EndReason | None = None,
) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        thread_id=thread_id,
        user_id="u1",
        graph_name="medical_consultation",
        graph_version="v1",
        status=status,
        end_reason=end_reason,
        payload_hash="h1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_timeout_sets_safe_close_timeout_and_runtime_materialized_response() -> None:
    queue = InMemoryReviewQueue()
    task = _task("t1", "th1")
    ticket = queue.create_or_get(
        task_id=task.task_id,
        thread_id=task.thread_id,
        reason="needs_human_review",
        interrupt_point="human_review_node",
        timeout_seconds=300,
    )
    updated_task, response = HumanReviewWatchdog(queue).handle_timeout(task, ticket.ticket_id)
    assert updated_task.status == TaskStatus.completed
    assert updated_task.end_reason == EndReason.safe_close_timeout
    assert response["materialized_by"] == "runtime_watchdog"
    assert queue.get(ticket.ticket_id).status == ReviewTicketStatus.timed_out


def test_late_normal_resume_is_rejected_after_timeout() -> None:
    queue = InMemoryReviewQueue()
    task = _task("t2", "th2", status=TaskStatus.completed, end_reason=EndReason.safe_close_timeout)
    ticket = queue.create_or_get(
        task_id=task.task_id,
        thread_id=task.thread_id,
        reason="needs_human_review",
        interrupt_point="human_review_node",
        timeout_seconds=300,
    )
    queue.mark_timed_out(ticket.ticket_id)

    with pytest.raises(LateResumeRejected):
        ResumeCoordinator(queue).resume(task, ticket.ticket_id, ReviewDecision.approve_continue)


def test_force_reopen_creates_child_task_and_new_checkpoint_chain(tmp_path: Path) -> None:
    store = SqliteRuntimeStore(db_path=tmp_path / "runtime.db", encryption_key="test-key")
    checkpointer = InProcessCheckpointer(store)

    original = _task(
        "t3",
        "th3",
        status=TaskStatus.completed,
        end_reason=EndReason.safe_close_timeout,
    )
    store.create_task(original, {"q": "hello"})
    checkpointer.save(
        task_id=original.task_id,
        thread_id=original.thread_id,
        graph_version=original.graph_version,
        state={"entry_node": "human_review", "step": 1},
    )

    reopened = force_reopen_task(original, reopen_reason="late_human_approval", new_task_id="t3-reopen")
    assert reopened.parent_task_id == original.task_id
    assert reopened.thread_id == original.thread_id
    assert reopened.status == TaskStatus.pending

    store.create_task(reopened, {"reopen_reason": "late_human_approval"})
    checkpointer.save(
        task_id=reopened.task_id,
        thread_id=reopened.thread_id,
        graph_version=reopened.graph_version,
        state={"entry_node": "triage", "step": 1},
    )

    latest_reopen = checkpointer.load_latest(reopened.task_id, reopened.thread_id)
    latest_original = checkpointer.load_latest(original.task_id, original.thread_id)
    assert latest_reopen is not None
    assert latest_original is not None
    assert latest_reopen["state"]["entry_node"] == "triage"
    assert latest_original["state"]["entry_node"] == "human_review"
    store.close()


def test_review_ticket_creation_is_idempotent_on_duplicate_interrupt() -> None:
    queue = InMemoryReviewQueue()
    ticket_a = queue.create_or_get(
        task_id="t4",
        thread_id="th4",
        reason="risk_violation",
        interrupt_point="safety_review_node",
        timeout_seconds=300,
    )
    ticket_b = queue.create_or_get(
        task_id="t4",
        thread_id="th4",
        reason="risk_violation",
        interrupt_point="safety_review_node",
        timeout_seconds=300,
    )
    assert ticket_a.ticket_id == ticket_b.ticket_id
    assert len(queue.list_by_task("t4")) == 1
