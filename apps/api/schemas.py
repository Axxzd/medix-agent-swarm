from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    user_id: str
    graph_name: str = "medical_consultation"
    graph_version: str = "v1"
    thread_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ThreadCreateRequest(BaseModel):
    thread_id: str | None = None


class ApprovalDecisionRequest(BaseModel):
    ticket_id: str
    decision: str
    reviewer_id: str
    notes: str | None = None


class ForceReopenRequest(BaseModel):
    reason: str
