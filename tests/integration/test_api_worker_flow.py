from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.deps import InMemoryRuntimeStore
from apps.api.main import create_app
from apps.worker.runner import WorkerRunner


def _mock_llm(**kwargs: object) -> str:
    _ = kwargs
    return "这是经由 LLM 推理生成的测试回答。"


def test_submit_poll_and_worker_complete_flow() -> None:
    runtime = InMemoryRuntimeStore()
    app = create_app(runtime=runtime)
    client = TestClient(app)
    worker = WorkerRunner(runtime=runtime, worker_id="w1", llm_generate=_mock_llm)

    resp = client.post(
        "/tasks",
        json={
            "user_id": "u1",
            "graph_name": "medical_consultation",
            "graph_version": "v1",
            "payload": {"question": "持续高热三天，伴明显呼吸急促"},
        },
    )
    assert resp.status_code == 202
    task_id = resp.json()["task_id"]

    status_before = client.get(f"/tasks/{task_id}")
    assert status_before.status_code == 200
    assert status_before.json()["status"] == "pending"

    worker.run_once()

    status_after = client.get(f"/tasks/{task_id}").json()
    assert status_after["status"] == "completed"

    result = client.get(f"/tasks/{task_id}/result").json()
    assert result["status"] == "completed"
    assert "answer" in result["result"]


def test_worker_retries_until_max_attempts_then_fails() -> None:
    runtime = InMemoryRuntimeStore(max_total_attempts=3)
    app = create_app(runtime=runtime)
    client = TestClient(app)
    worker = WorkerRunner(runtime=runtime, worker_id="w1", llm_generate=_mock_llm)

    resp = client.post(
        "/tasks",
        json={
            "user_id": "u1",
            "graph_name": "medical_consultation",
            "graph_version": "v1",
            "payload": {"question": "test", "force_worker_error": True},
        },
    )
    task_id = resp.json()["task_id"]

    worker.run_once()
    worker.run_once()
    worker.run_once()

    status = client.get(f"/tasks/{task_id}").json()
    assert status["status"] == "failed"
    assert status["attempt_count"] == 3


def test_claim_lease_and_heartbeat_updates_runtime_state() -> None:
    runtime = InMemoryRuntimeStore(claim_lease_seconds=30)
    app = create_app(runtime=runtime)
    client = TestClient(app)

    resp = client.post(
        "/tasks",
        json={
            "user_id": "u1",
            "graph_name": "medical_consultation",
            "graph_version": "v1",
            "payload": {"question": "普通咨询"},
        },
    )
    task_id = resp.json()["task_id"]

    claimed = runtime.claim_next(worker_id="w1")
    assert claimed is not None
    assert claimed.status == "claimed"
    assert claimed.lease_expires_at is not None

    runtime.heartbeat(task_id, worker_id="w1")
    updated = runtime.get_task(task_id)
    assert updated is not None
    assert updated.heartbeat_at is not None
