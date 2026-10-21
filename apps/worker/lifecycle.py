from __future__ import annotations

from apps.worker.runner import WorkerRunner


class WorkerLifecycle:
    def __init__(self, runner: WorkerRunner) -> None:
        self.runner = runner

    def tick(self) -> bool:
        task = self.runner.run_once()
        return task is not None
