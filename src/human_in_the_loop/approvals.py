from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime

from src.contracts.tasks import TaskRecord, TaskStatus


def force_reopen_task(
    original_task: TaskRecord,
    *,
    reopen_reason: str,
    new_task_id: str | None = None,
) -> TaskRecord:
    payload = dict(original_task.payload)
    payload["reopen_reason"] = reopen_reason
    payload["reopened_from_task_id"] = original_task.task_id
    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    now = datetime.utcnow()
    return TaskRecord(
        task_id=new_task_id or f"task_{uuid.uuid4().hex}",
        parent_task_id=original_task.task_id,
        thread_id=original_task.thread_id,
        user_id=original_task.user_id,
        graph_name=original_task.graph_name,
        graph_version=original_task.graph_version,
        status=TaskStatus.pending,
        end_reason=None,
        payload=payload,
        payload_hash=payload_hash,
        created_at=now,
        updated_at=now,
    )
