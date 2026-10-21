from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from apps.api.deps import InMemoryRuntimeStore, RuntimeTask
from src.config.settings import AppSettings
from src.graphs.medical_consultation.graph import build_medical_consultation_graph
from src.graphs.medical_consultation.state import create_initial_state
from src.models import build_llm_generate_from_settings


class WorkerRunner:
    def __init__(
        self,
        *,
        runtime: InMemoryRuntimeStore,
        worker_id: str,
        llm_generate: Callable[..., str] | None = None,
    ) -> None:
        self.runtime = runtime
        self.worker_id = worker_id
        self._llm_generate = llm_generate

    def run_once(self) -> RuntimeTask | None:
        task = self.runtime.claim_next(worker_id=self.worker_id)
        if task is None:
            return None

        self.runtime.mark_running(task.task_id, worker_id=self.worker_id)
        self.runtime.heartbeat(task.task_id, worker_id=self.worker_id)

        try:
            if bool(task.payload.get("force_worker_error")):
                raise RuntimeError("forced_worker_error")

            graph = build_medical_consultation_graph(graph_version=task.graph_version)
            state = create_initial_state(
                task_id=task.task_id,
                thread_id=task.thread_id,
                user_id=task.user_id,
                trace_id=f"tr_{task.task_id}",
                question=str(task.payload.get("question") or ""),
                graph_name=task.graph_name,
                graph_version=task.graph_version,
            )
            llm_generate = self._llm_generate or build_llm_generate_from_settings(AppSettings())
            result_state = graph.invoke(
                state,
                services={
                    "llm_generate": llm_generate,
                },
            )
            final_response = dict(result_state.get("final_response") or {})
            end_reason = str(result_state.get("end_reason") or "normal_finalize")
            self.runtime.mark_completed(
                task.task_id,
                result=final_response,
                end_reason=end_reason,
            )
        except Exception as exc:
            self.runtime.mark_retry_or_failed(task.task_id, error=str(exc))
        finally:
            current = self.runtime.get_task(task.task_id)
            if current is not None:
                current.updated_at = datetime.utcnow()
        return self.runtime.get_task(task.task_id)
