from __future__ import annotations

from fastapi import APIRouter, Request

from apps.api.schemas import ThreadCreateRequest

router = APIRouter(tags=["threads"])


@router.post("/threads")
def create_thread(body: ThreadCreateRequest, request: Request) -> dict:
    runtime = request.app.state.runtime
    thread_id = runtime.create_thread(thread_id=body.thread_id)
    return {"thread_id": thread_id}
