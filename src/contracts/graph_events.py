from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class GraphEventType(StrEnum):
    node_started = "node_started"
    node_completed = "node_completed"
    tool_called = "tool_called"
    model_called = "model_called"
    interrupted = "interrupted"
    resumed = "resumed"
    failed = "failed"
    completed = "completed"


class GraphEvent(BaseModel):
    event_id: str
    task_id: str
    thread_id: str
    trace_id: str
    event_type: GraphEventType
    node_name: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
