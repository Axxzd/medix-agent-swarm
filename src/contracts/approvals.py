from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ReviewDecision(StrEnum):
    approve_continue = "approve_continue"
    safe_close = "safe_close"
    force_reopen = "force_reopen"


class ReviewTicketStatus(StrEnum):
    pending = "pending"
    claimed = "claimed"
    resolved = "resolved"
    timed_out = "timed_out"
    expired = "expired"


class ReviewTicket(BaseModel):
    ticket_id: str
    task_id: str
    thread_id: str
    reason: str
    priority: str = "normal"
    status: ReviewTicketStatus = ReviewTicketStatus.pending
    reviewer_id: str | None = None
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewDecisionRequest(BaseModel):
    ticket_id: str
    decision: ReviewDecision
    reviewer_id: str
    review_notes: str = Field(min_length=1)
