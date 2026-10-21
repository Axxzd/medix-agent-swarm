from __future__ import annotations

from src.contracts.approvals import ReviewTicket
from src.human_in_the_loop.review_queue import InMemoryReviewQueue


class HumanInterruptService:
    def __init__(self, queue: InMemoryReviewQueue) -> None:
        self._queue = queue

    def create_ticket(
        self,
        *,
        task_id: str,
        thread_id: str,
        reason: str,
        interrupt_point: str,
        timeout_seconds: int,
        priority: str = "normal",
    ) -> ReviewTicket:
        return self._queue.create_or_get(
            task_id=task_id,
            thread_id=thread_id,
            reason=reason,
            interrupt_point=interrupt_point,
            timeout_seconds=timeout_seconds,
            priority=priority,
        )
