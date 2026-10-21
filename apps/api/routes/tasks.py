from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from apps.api.schemas import TaskCreateRequest

router = APIRouter(tags=["tasks"])


@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
def create_task(body: TaskCreateRequest, request: Request) -> dict:
    runtime = request.app.state.runtime
    task = runtime.create_task(
        user_id=body.user_id,
        graph_name=body.graph_name,
        graph_version=body.graph_version,
        payload=body.payload,
        thread_id=body.thread_id,
    )
    return {
        "task_id": task.task_id,
        "thread_id": task.thread_id,
        "status": task.status,
    }


@router.get("/tasks/{task_id}")
def get_task(task_id: str, request: Request) -> dict:
    runtime = request.app.state.runtime
    task = runtime.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return runtime.to_public(task)


@router.get("/tasks/{task_id}/result")
def get_task_result(task_id: str, request: Request) -> dict:
    runtime = request.app.state.runtime
    task = runtime.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "end_reason": task.end_reason,
        "result": task.result,
    }


@router.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str, request: Request) -> dict:
    runtime = request.app.state.runtime
    task = runtime.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    updated = runtime.cancel_task(task_id)
    return runtime.to_public(updated)
