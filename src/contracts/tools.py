from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolResultStatus(StrEnum):
    ok = "ok"
    error = "error"
    denied = "denied"
    timeout = "timeout"


class ToolResult(BaseModel):
    status: ToolResultStatus
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class ToolCallRecord(BaseModel):
    task_id: str
    thread_id: str
    trace_id: str
    tool_name: str
    status: ToolResultStatus
    duration_ms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
