from __future__ import annotations

from typing import Any

from src.persistence.stores import SqliteRuntimeStore


class ReplayService:
    def __init__(self, store: SqliteRuntimeStore) -> None:
        self._store = store

    def latest(self, task_id: str, thread_id: str) -> dict[str, Any] | None:
        return self._store.load_latest_checkpoint(task_id, thread_id)
