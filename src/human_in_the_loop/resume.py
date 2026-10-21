from __future__ import annotations

from datetime import datetime
from typing import Any

from src.contracts.approvals import ReviewDecision, ReviewTicketStatus
from src.contracts.tasks import EndReason, TaskRecord, TaskStatus
from src.human_in_the_loop.review_queue import InMemoryReviewQueue


class LateResumeRejected(RuntimeError):
    pass


class HumanReviewWatchdog:
    def __init__(self, queue: InMemoryReviewQueue) -> None:
        self._queue = queue

    def handle_timeout(
        self, task: TaskRecord, ticket_id: str
    ) -> tuple[TaskRecord, dict[str, Any]]:
        self._queue.mark_timed_out(ticket_id)
        if task.status == TaskStatus.completed and task.end_reason == EndReason.safe_close_timeout:
            return task, _runtime_safe_close_response(task)

        updated_task = task.model_copy(
            update={
                "status": TaskStatus.completed,
                "end_reason": EndReason.safe_close_timeout,
                "updated_at": datetime.utcnow(),
            }
        )
        response = _runtime_safe_close_response(updated_task)
        return updated_task, response


class ResumeCoordinator:
    def __init__(self, queue: InMemoryReviewQueue) -> None:
        self._queue = queue

    def resume(
        self, task: TaskRecord, ticket_id: str, decision: ReviewDecision
    ) -> dict[str, Any]:
        ticket = self._queue.get(ticket_id)

        if ticket.status == ReviewTicketStatus.timed_out and decision != ReviewDecision.force_reopen:
            raise LateResumeRejected(
                "Review ticket timed out. Normal resume is rejected; force_reopen is required."
            )

        self._queue.mark_resolved(ticket_id)
        if decision == ReviewDecision.approve_continue:
            return {"next_node": "triage", "status": TaskStatus.running.value}
        if decision == ReviewDecision.safe_close:
            return {
                "next_node": "final_response",
                "status": TaskStatus.completed.value,
                "end_reason": EndReason.safe_close_human.value,
            }
        if decision == ReviewDecision.force_reopen:
            return {
                "next_node": "force_reopen",
                "parent_task_id": task.task_id,
                "thread_id": task.thread_id,
            }
        raise ValueError(f"Unsupported review decision: {decision!r}")


def _runtime_safe_close_response(task: TaskRecord) -> dict[str, Any]:
    return {
        "answer": "人工审核超时。为安全起见，请尽快联系线下医生或急诊服务。",
        "risk_level": "high",
        "end_reason": task.end_reason.value if task.end_reason else None,
        "materialized_by": "runtime_watchdog",
    }
