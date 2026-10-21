from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from apps.api.schemas import ApprovalDecisionRequest, ForceReopenRequest

router = APIRouter(tags=["approvals"])


@router.post("/review-tickets/{ticket_id}/decision")
def decide_review(ticket_id: str, body: ApprovalDecisionRequest, request: Request) -> dict:
    runtime = request.app.state.runtime
    ticket = runtime.review_tickets.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="review ticket not found")
    ticket["decision"] = body.decision
    ticket["reviewer_id"] = body.reviewer_id
    ticket["notes"] = body.notes
    ticket["status"] = "resolved"
    return {"ticket_id": ticket_id, "status": "resolved"}


@router.post("/tasks/{task_id}/force-reopen")
def force_reopen(task_id: str, body: ForceReopenRequest, request: Request) -> dict:
    runtime = request.app.state.runtime
    task = runtime.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.thread_id not in runtime.threads:
        runtime.threads.add(task.thread_id)
    new_task = runtime.create_task(
        user_id=task.user_id,
        graph_name=task.graph_name,
        graph_version=task.graph_version,
        payload={**task.payload, "reopen_reason": body.reason, "parent_task_id": task_id},
        thread_id=task.thread_id,
    )
    return {"task_id": new_task.task_id, "parent_task_id": task_id, "thread_id": task.thread_id}
