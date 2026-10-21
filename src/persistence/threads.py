from __future__ import annotations

import uuid

from src.persistence.stores import SqliteRuntimeStore


class ThreadService:
    def __init__(self, store: SqliteRuntimeStore) -> None:
        self._store = store

    def create_thread(self, user_id: str, *, requested_thread_id: str | None = None) -> str:
        thread_id = requested_thread_id or f"th_{uuid.uuid4().hex}"
        self._store.upsert_thread(thread_id=thread_id, user_id=user_id)
        return thread_id
