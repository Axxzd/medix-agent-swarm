from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class RuntimeTask:
    task_id: str
    thread_id: str
    user_id: str
    graph_name: str
    graph_version: str
    payload: dict[str, Any]
    status: str = "pending"
    end_reason: str | None = None
    result: dict[str, Any] | None = None
    attempt_count: int = 0
    worker_id: str | None = None
    lease_expires_at: datetime | None = None
    heartbeat_at: datetime | None = None
    last_error: str | None = None
    cancellation_requested: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryRuntimeStore:
    def __init__(
        self,
        *,
        claim_lease_seconds: int = 30,
        heartbeat_every_seconds: int = 10,
        max_total_attempts: int = 3,
    ) -> None:
        self.claim_lease_seconds = claim_lease_seconds
        self.heartbeat_every_seconds = heartbeat_every_seconds
        self.max_total_attempts = max_total_attempts
        self.tasks: dict[str, RuntimeTask] = {}
        self.threads: set[str] = set()
        self.review_tickets: dict[str, dict[str, Any]] = {}

    def create_thread(self, thread_id: str | None = None) -> str:
        tid = thread_id or f"th_{uuid.uuid4().hex}"
        self.threads.add(tid)
        return tid

    def create_task(
        self,
        *,
        user_id: str,
        graph_name: str,
        graph_version: str,
        payload: dict[str, Any],
        thread_id: str | None = None,
    ) -> RuntimeTask:
        task_id = f"task_{uuid.uuid4().hex}"
        tid = thread_id or self.create_thread()
        now = datetime.utcnow()
        task = RuntimeTask(
            task_id=task_id,
            thread_id=tid,
            user_id=user_id,
            graph_name=graph_name,
            graph_version=graph_version,
            payload=dict(payload),
            created_at=now,
            updated_at=now,
        )
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> RuntimeTask | None:
        return self.tasks.get(task_id)

    def claim_next(self, *, worker_id: str) -> RuntimeTask | None:
        now = datetime.utcnow()
        for task in self.tasks.values():
            lease_expired = task.lease_expires_at is not None and task.lease_expires_at <= now
            if task.status == "pending" or (task.status == "claimed" and lease_expired):
                task.status = "claimed"
                task.worker_id = worker_id
                task.attempt_count += 1
                task.lease_expires_at = now + timedelta(seconds=self.claim_lease_seconds)
                task.updated_at = now
                return task
        return None

    def heartbeat(self, task_id: str, *, worker_id: str) -> None:
        task = self.tasks[task_id]
        if task.worker_id != worker_id:
            return
        now = datetime.utcnow()
        task.heartbeat_at = now
        task.lease_expires_at = now + timedelta(seconds=self.claim_lease_seconds)
        task.updated_at = now

    def mark_running(self, task_id: str, *, worker_id: str) -> None:
        task = self.tasks[task_id]
        task.status = "running"
        task.worker_id = worker_id
        task.updated_at = datetime.utcnow()

    def mark_completed(self, task_id: str, *, result: dict[str, Any], end_reason: str) -> None:
        task = self.tasks[task_id]
        task.status = "completed"
        task.end_reason = end_reason
        task.result = result
        task.updated_at = datetime.utcnow()

    def mark_retry_or_failed(self, task_id: str, *, error: str) -> None:
        task = self.tasks[task_id]
        task.last_error = error
        task.updated_at = datetime.utcnow()
        if task.attempt_count >= self.max_total_attempts:
            task.status = "failed"
            task.end_reason = "failed_runtime"
        else:
            task.status = "pending"

    def cancel_task(self, task_id: str) -> RuntimeTask:
        task = self.tasks[task_id]
        if task.status == "pending":
            task.status = "cancelled"
            task.end_reason = "cancelled_by_user"
        elif task.status in {"claimed", "running"}:
            task.cancellation_requested = True
        elif task.status == "interrupted":
            task.status = "cancelled"
            task.end_reason = "cancelled_by_user"
        task.updated_at = datetime.utcnow()
        return task

    def to_public(self, task: RuntimeTask) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "thread_id": task.thread_id,
            "status": task.status,
            "end_reason": task.end_reason,
            "attempt_count": task.attempt_count,
            "cancellation_requested": task.cancellation_requested,
        }
