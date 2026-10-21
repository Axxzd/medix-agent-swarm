from __future__ import annotations

from datetime import datetime

from src.contracts.tasks import EndReason, TaskRecord, TaskStatus


_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.pending: {TaskStatus.claimed, TaskStatus.cancelled},
    TaskStatus.claimed: {TaskStatus.running, TaskStatus.failed, TaskStatus.pending},
    TaskStatus.running: {
        TaskStatus.interrupted,
        TaskStatus.completed,
        TaskStatus.failed,
        TaskStatus.cancelled,
    },
    TaskStatus.interrupted: {
        TaskStatus.running,
        TaskStatus.completed,
        TaskStatus.failed,
        TaskStatus.cancelled,
    },
    TaskStatus.completed: set(),
    TaskStatus.failed: set(),
    TaskStatus.cancelled: set(),
}

_TERMINAL_STATUSES = {TaskStatus.completed, TaskStatus.failed, TaskStatus.cancelled}


def can_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    return to_status in _TRANSITIONS[from_status]


def transition_task(
    task: TaskRecord,
    to_status: TaskStatus,
    *,
    end_reason: EndReason | None = None,
) -> TaskRecord:
    if not can_transition(task.status, to_status):
        raise ValueError(f"Invalid status transition: {task.status} -> {to_status}")

    if to_status == TaskStatus.completed and end_reason is None:
        raise ValueError("Transition to completed requires an explicit end_reason.")

    return task.model_copy(
        update={
            "status": to_status,
            "end_reason": end_reason if end_reason is not None else task.end_reason,
            "updated_at": datetime.utcnow(),
        }
    )


def cancel_task(task: TaskRecord) -> tuple[TaskRecord, dict[str, bool]]:
    close_review_ticket = False

    if task.status == TaskStatus.pending:
        cancelled = transition_task(
            task, TaskStatus.cancelled, end_reason=EndReason.cancelled_by_user
        )
        return cancelled, {"close_review_ticket": close_review_ticket}

    if task.status in {TaskStatus.claimed, TaskStatus.running}:
        payload = dict(task.payload)
        payload["cancellation_requested"] = True
        updated = task.model_copy(
            update={
                "payload": payload,
                "updated_at": datetime.utcnow(),
            }
        )
        return updated, {"close_review_ticket": close_review_ticket}

    if task.status == TaskStatus.interrupted:
        close_review_ticket = True
        cancelled = transition_task(
            task, TaskStatus.cancelled, end_reason=EndReason.cancelled_by_user
        )
        return cancelled, {"close_review_ticket": close_review_ticket}

    if task.status in _TERMINAL_STATUSES:
        raise ValueError(f"Cannot cancel terminal task in status: {task.status}")

    raise ValueError(f"Unknown task status: {task.status}")
