from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contracts.tasks import TaskRecord, TaskStatus
from src.persistence.checkpointers import InProcessCheckpointer, validate_backend_policy
from src.persistence.replay import ReplayService
from src.persistence.stores import SqliteRuntimeStore
from src.persistence.threads import ThreadService


def _task(task_id: str, thread_id: str) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        thread_id=thread_id,
        user_id="u1",
        graph_name="medical_consultation",
        graph_version="v1",
        status=TaskStatus.pending,
        payload_hash="h1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_runtime_store_creates_minimum_required_tables(tmp_path: Path) -> None:
    store = SqliteRuntimeStore(db_path=tmp_path / "runtime.db", encryption_key="test-key")
    tables = store.list_tables()
    required = {"tasks", "task_events", "review_tickets", "checkpoints", "audit_events"}
    assert required.issubset(tables)
    store.close()


def test_payload_is_encrypted_at_rest_and_roundtrips(tmp_path: Path) -> None:
    store = SqliteRuntimeStore(db_path=tmp_path / "runtime.db", encryption_key="test-key")
    task = _task("t1", "th1")
    payload = {"patient_name": "Alice", "symptom": "fever"}
    store.create_task(task, payload)

    raw = store.raw_payload_blob(task.task_id)
    assert raw is not None
    assert "Alice" not in raw
    assert "fever" not in raw

    loaded = store.fetch_task(task.task_id)
    assert loaded is not None
    assert loaded.payload == payload
    store.close()


def test_checkpoint_resume_and_replay_latest(tmp_path: Path) -> None:
    store = SqliteRuntimeStore(db_path=tmp_path / "runtime.db", encryption_key="test-key")
    thread_service = ThreadService(store)
    thread_id = thread_service.create_thread("u1", requested_thread_id="th-1")
    task = _task("t-replay", thread_id)
    store.create_task(task, {"q": "hello"})

    checkpointer = InProcessCheckpointer(store)
    checkpointer.save(
        task_id=task.task_id,
        thread_id=thread_id,
        graph_version="v1",
        state={"step": 1, "note": "first"},
    )
    checkpointer.save(
        task_id=task.task_id,
        thread_id=thread_id,
        graph_version="v1",
        state={"step": 2, "note": "second"},
    )

    latest = checkpointer.load_latest(task.task_id, thread_id)
    assert latest is not None
    assert latest["state"]["step"] == 2

    replay = ReplayService(store).latest(task.task_id, thread_id)
    assert replay is not None
    assert replay["state"]["note"] == "second"
    store.close()


def test_validate_backend_policy_requires_postgres_in_prod() -> None:
    dev_settings = SimpleNamespace(app_env="dev", checkpoint_backend="sqlite")
    validate_backend_policy(dev_settings)

    prod_settings = SimpleNamespace(app_env="prod", checkpoint_backend="sqlite")
    try:
        validate_backend_policy(prod_settings)
        assert False, "Expected ValueError in prod when backend is not postgres."
    except ValueError as exc:
        assert "postgres" in str(exc).lower()
