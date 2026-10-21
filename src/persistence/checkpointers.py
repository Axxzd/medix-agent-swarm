from __future__ import annotations

from typing import Any

from src.persistence.stores import SqliteRuntimeStore


def validate_backend_policy(settings: Any) -> None:
    if settings.app_env == "prod" and settings.checkpoint_backend != "postgres":
        raise ValueError("checkpoint backend must be postgres in prod.")


class InProcessCheckpointer:
    def __init__(self, store: SqliteRuntimeStore) -> None:
        self._store = store

    def save(
        self,
        *,
        task_id: str,
        thread_id: str,
        graph_version: str,
        state: dict[str, Any],
    ) -> int:
        return self._store.save_checkpoint(
            task_id=task_id,
            thread_id=thread_id,
            graph_version=graph_version,
            state=state,
        )

    def load_latest(self, task_id: str, thread_id: str) -> dict[str, Any] | None:
        return self._store.load_latest_checkpoint(task_id, thread_id)
