from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path

import uvicorn

# Ensure project root is importable when running:
# `python scripts/run_dev_stack.py`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.api.deps import InMemoryRuntimeStore
from apps.api.main import create_app
from apps.worker.runner import WorkerRunner


def _worker_loop(runner: WorkerRunner, stop_event: threading.Event, interval_seconds: float) -> None:
    while not stop_event.is_set():
        runner.run_once()
        stop_event.wait(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local API+Worker dev stack in one process.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--worker-interval", type=float, default=0.2)
    args = parser.parse_args()

    runtime = InMemoryRuntimeStore()
    app = create_app(runtime=runtime)
    runner = WorkerRunner(runtime=runtime, worker_id="dev-worker-1")

    stop_event = threading.Event()
    worker_thread = threading.Thread(
        target=_worker_loop,
        args=(runner, stop_event, args.worker_interval),
        daemon=True,
    )
    worker_thread.start()

    try:
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    finally:
        stop_event.set()
        worker_thread.join(timeout=2)


if __name__ == "__main__":
    main()
