from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contracts.tasks import EndReason, TaskRecord, TaskStatus
from src.tasks.lifecycle import cancel_task, transition_task


def _task(status: TaskStatus) -> TaskRecord:
    return TaskRecord(
        task_id="t1",
        thread_id="th1",
        user_id="u1",
        graph_name="medical_consultation",
        graph_version="v1",
        status=status,
        payload_hash="hash1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_transition_task_allows_contract_path() -> None:
    task = _task(TaskStatus.pending)
    claimed = transition_task(task, TaskStatus.claimed)
    assert claimed.status == TaskStatus.claimed

    running = transition_task(claimed, TaskStatus.running)
    assert running.status == TaskStatus.running

    done = transition_task(
        running,
        TaskStatus.completed,
        end_reason=EndReason.normal_finalize,
    )
    assert done.status == TaskStatus.completed
    assert done.end_reason == EndReason.normal_finalize


def test_transition_task_rejects_invalid_path() -> None:
    task = _task(TaskStatus.completed)
    with pytest.raises(ValueError):
        transition_task(task, TaskStatus.running)


def test_transition_to_completed_requires_end_reason() -> None:
    task = _task(TaskStatus.running)
    with pytest.raises(ValueError):
        transition_task(task, TaskStatus.completed)


def test_cancel_task_pending_immediate_cancel() -> None:
    task = _task(TaskStatus.pending)
    cancelled, action = cancel_task(task)
    assert cancelled.status == TaskStatus.cancelled
    assert cancelled.end_reason == EndReason.cancelled_by_user
    assert action["close_review_ticket"] is False


def test_cancel_task_running_sets_cancellation_requested() -> None:
    task = _task(TaskStatus.running)
    next_task, action = cancel_task(task)
    assert next_task.status == TaskStatus.running
    assert next_task.payload["cancellation_requested"] is True
    assert action["close_review_ticket"] is False


def test_cancel_task_interrupted_closes_review_ticket() -> None:
    task = _task(TaskStatus.interrupted)
    cancelled, action = cancel_task(task)
    assert cancelled.status == TaskStatus.cancelled
    assert cancelled.end_reason == EndReason.cancelled_by_user
    assert action["close_review_ticket"] is True


def test_cancel_task_rejects_terminal_state() -> None:
    task = _task(TaskStatus.failed)
    with pytest.raises(ValueError):
        cancel_task(task)
