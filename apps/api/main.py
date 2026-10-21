from __future__ import annotations

from fastapi import FastAPI

from apps.api.deps import InMemoryRuntimeStore
from apps.api.routes.approvals import router as approvals_router
from apps.api.routes.tasks import router as tasks_router
from apps.api.routes.threads import router as threads_router


def create_app(*, runtime: InMemoryRuntimeStore | None = None) -> FastAPI:
    app = FastAPI(title="medix-agent-swarm-api")
    app.state.runtime = runtime or InMemoryRuntimeStore()
    app.include_router(tasks_router)
    app.include_router(threads_router)
    app.include_router(approvals_router)
    return app


app = create_app()
