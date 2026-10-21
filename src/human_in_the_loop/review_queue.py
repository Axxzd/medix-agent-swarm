from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from src.contracts.approvals import ReviewTicket, ReviewTicketStatus


class InMemoryReviewQueue:
    def __init__(self) -> None:
        self._tickets: dict[str, ReviewTicket] = {}
        self._idempotency_index: dict[tuple[str, str, str], str] = {}

    def create_or_get(
        self,
        *,
        task_id: str,
        thread_id: str,
        reason: str,
        interrupt_point: str,
        timeout_seconds: int,
        priority: str = "normal",
    ) -> ReviewTicket:
        key = (task_id, interrupt_point, reason)
        existing_id = self._idempotency_index.get(key)
        if existing_id is not None:
            return self._tickets[existing_id]

        now = datetime.utcnow()
        ticket = ReviewTicket(
            ticket_id=f"rt_{uuid.uuid4().hex}",
            task_id=task_id,
            thread_id=thread_id,
            reason=reason,
            priority=priority,
            status=ReviewTicketStatus.pending,
            expires_at=now + timedelta(seconds=timeout_seconds),
            created_at=now,
            updated_at=now,
        )
        self._tickets[ticket.ticket_id] = ticket
        self._idempotency_index[key] = ticket.ticket_id
        return ticket

    def get(self, ticket_id: str) -> ReviewTicket:
        return self._tickets[ticket_id]

    def mark_timed_out(self, ticket_id: str) -> ReviewTicket:
        ticket = self._tickets[ticket_id]
        updated = ticket.model_copy(
            update={
                "status": ReviewTicketStatus.timed_out,
                "updated_at": datetime.utcnow(),
            }
        )
        self._tickets[ticket_id] = updated
        return updated

    def mark_resolved(self, ticket_id: str) -> ReviewTicket:
        ticket = self._tickets[ticket_id]
        updated = ticket.model_copy(
            update={
                "status": ReviewTicketStatus.resolved,
                "updated_at": datetime.utcnow(),
            }
        )
        self._tickets[ticket_id] = updated
        return updated

    def list_by_task(self, task_id: str) -> list[ReviewTicket]:
        return [ticket for ticket in self._tickets.values() if ticket.task_id == task_id]
