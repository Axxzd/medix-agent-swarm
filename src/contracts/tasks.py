from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    pending = "pending"
    claimed = "claimed"
    running = "running"
    interrupted = "interrupted"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class EndReason(StrEnum):
    emergency = "emergency"
    safe_close_timeout = "safe_close_timeout"
    safe_close_human = "safe_close_human"
    normal_finalize = "normal_finalize"
    cancelled_by_user = "cancelled_by_user"
    failed_runtime = "failed_runtime"


class TaskRecord(BaseModel):
    task_id: str
    parent_task_id: str | None = None
    thread_id: str
    user_id: str
    graph_name: str
    graph_version: str
    status: TaskStatus = TaskStatus.pending
    end_reason: EndReason | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    payload_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateTaskRequest(BaseModel):
    user_id: str
    thread_id: str | None = None
    graph_name: str = "medical_consultation"
    graph_version: str = "v1"
    payload: dict[str, Any] = Field(default_factory=dict)


class CreateTaskResponse(BaseModel):
    task_id: str
    thread_id: str
    status: TaskStatus
    idempotent_hit: bool = False
