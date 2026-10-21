from __future__ import annotations

from apps.api.deps import InMemoryRuntimeStore
from apps.worker.lifecycle import WorkerLifecycle
from apps.worker.runner import WorkerRunner


def build_worker(*, runtime: InMemoryRuntimeStore, worker_id: str = "worker-1") -> WorkerLifecycle:
    runner = WorkerRunner(runtime=runtime, worker_id=worker_id)
    return WorkerLifecycle(runner)
