# LangGraph Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a production-grade LangGraph medical consultation runtime slice in `medix-agent-swarm` according to `docs/langgraph-implementation-contract.md`.

**Architecture:** Build the system in thin vertical slices: config/contracts -> graph state/routing -> task lifecycle -> core nodes -> persistence/HITL -> API/worker -> observability/evals. Lock routing and lifecycle behavior with tests before node logic expansion.

**Tech Stack:** Python 3.12, LangGraph, Pydantic v2, pydantic-settings, SQLAlchemy 2.x, Alembic, pytest.

---

### Execution Order Override (Authoritative)

Run tasks in this exact order even if task numbers differ:

1. Task 1
2. Task 2
3. Task 3
4. Task 5
5. Task 6
6. Task 4
7. Task 7
8. Task 8
9. Task 10
10. Task 9
11. Task 11
12. Task 12
13. Task 13
14. Task 14
15. Task 15

### Task 1: Project Scaffolding and Package Layout

**Files:**
- Create: `src/__init__.py`
- Create: `src/config/__init__.py`
- Create: `src/contracts/__init__.py`
- Create: `src/graphs/__init__.py`
- Create: `src/graphs/medical_consultation/__init__.py`
- Create: `src/graphs/medical_consultation/nodes/__init__.py`
- Create: `src/tasks/__init__.py`
- Create: `src/human_in_the_loop/__init__.py`
- Create: `src/guardrails/__init__.py`
- Create: `src/persistence/__init__.py`
- Create: `src/observability/__init__.py`
- Create: `tests/graph/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/safety/__init__.py`

- [ ] Step 1: Create empty package files.
- [ ] Step 2: Run import smoke check.
Run: `python -c "import src; import src.graphs; import src.config; print('ok')"`
Expected: `ok`
- [ ] Step 3: Commit.

### Task 2: Runtime Settings and Environment Validation

**Files:**
- Create: `src/config/settings.py`
- Create: `src/config/environments.py`
- Create: `src/config/feature_flags.py`
- Create: `src/config/graph_versions.py`
- Create: `.env.example`
- Test: `tests/unit/test_settings.py`

- [ ] Step 1: Write failing tests for config priority and prod fail-fast.
Run: `pytest tests/unit/test_settings.py -q`
Expected: missing module or failing assertions.
- [ ] Step 2: Implement settings with precedence: env vars > `.env` > defaults.
- [ ] Step 3: Implement prod validation for `llm_api_key`, `db_url`, and postgres checkpointer.
- [ ] Step 4: Re-run tests.
Run: `pytest tests/unit/test_settings.py -q`
Expected: pass.
- [ ] Step 5: Commit.

### Task 3: Core Contracts (Pydantic Boundaries)

**Files:**
- Create: `src/contracts/tasks.py`
- Create: `src/contracts/approvals.py`
- Create: `src/contracts/outputs.py`
- Create: `src/contracts/tools.py`
- Create: `src/contracts/graph_events.py`
- Test: `tests/unit/test_contracts.py`

- [ ] Step 1: Write failing tests for schema constraints:
  - citation excerpt max length
  - optional published date
  - task status enums
  - end reason enums
- [ ] Step 2: Implement contract models.
- [ ] Step 3: Re-run tests.
Run: `pytest tests/unit/test_contracts.py -q`
Expected: pass.
- [ ] Step 4: Commit.

### Task 4: Task Lifecycle and Transition Table

**Files:**
- Create: `src/tasks/model.py`
- Create: `src/tasks/lifecycle.py`
- Create: `src/tasks/store.py`
- Create: `src/tasks/claim.py`
- Test: `tests/unit/test_task_lifecycle.py`

- [ ] Step 1: Write failing tests for allowed/forbidden transitions.
- [ ] Step 2: Implement transition validator according to contract table.
- [ ] Step 3: Add cancellation behavior by state.
- [ ] Step 4: Re-run lifecycle tests.
Run: `pytest tests/unit/test_task_lifecycle.py -q`
Expected: pass.
- [ ] Step 5: Commit.

### Task 5: Graph State Schema and Reducers

**Files:**
- Create: `src/state/reducers.py`
- Create: `src/state/serializers.py`
- Create: `src/state/migrations.py`
- Create: `src/graphs/medical_consultation/state.py`
- Test: `tests/graph/test_state_reducers.py`

- [ ] Step 1: Write failing tests for overwrite/append/dedup reducer behavior.
- [ ] Step 2: Implement reducer functions with dedup keys for citations/evidence/events.
- [ ] Step 3: Implement medical graph typed state keys.
- [ ] Step 4: Re-run tests.
Run: `pytest tests/graph/test_state_reducers.py -q`
Expected: pass.
- [ ] Step 5: Commit.

### Task 6: Routing Functions and Edge Regression Tests

**Files:**
- Create: `src/graphs/medical_consultation/routing.py`
- Test: `tests/graph/test_routing.py`

- [ ] Step 1: Write failing routing tests from canonical edge table:
  - emergency precheck
  - unresolved intent
  - medical info no symptoms
  - high/medium/low risk
  - consultation next_action routing
  - human review decisions
- [ ] Step 2: Implement pure routing functions.
- [ ] Step 3: Re-run tests.
Run: `pytest tests/graph/test_routing.py -q`
Expected: pass.
- [ ] Step 4: Commit.

### Task 7: Tool Base and Registry

**Files:**
- Create: `src/tools/base.py`
- Create: `src/tools/registry.py`
- Test: `tests/unit/test_tool_registry.py`

- [ ] Step 1: Write failing tests for:
  - denied returns status `denied`
  - unknown tool returns `tool_not_found`
  - timeout classification and retry count policy
- [ ] Step 2: Implement async tool protocol and result envelope.
- [ ] Step 3: Implement registry behavior and timeout retry orchestration hook points.
- [ ] Step 4: Re-run tests.
Run: `pytest tests/unit/test_tool_registry.py -q`
Expected: pass.
- [ ] Step 5: Commit.

### Task 8: Guardrails and Citation Enforcement

**Files:**
- Create: `src/guardrails/medical_policy.py`
- Create: `src/guardrails/output_policy.py`
- Create: `src/guardrails/permissions.py`
- Create: `src/guardrails/sandbox.py`
- Create: `src/guardrails/secrets.py`
- Create: `src/guardrails/audit.py`
- Test: `tests/safety/test_medical_guardrails.py`

- [ ] Step 1: Write failing safety tests:
  - definitive diagnosis blocked
  - dosage advice blocked
  - emergency de-escalation blocked
  - special population medication advice blocked
  - required citation classes enforced
  - evidence source allowlist enforced
  - evidence source denylist blocked
- [ ] Step 2: Implement policy checks and severity mapping.
- [ ] Step 3: Re-run tests.
Run: `pytest tests/safety/test_medical_guardrails.py -q`
Expected: pass.
- [ ] Step 4: Commit.

### Task 9: HITL Queue, Timeout Watchdog, and Reopen Flow

**Files:**
- Create: `src/human_in_the_loop/interrupts.py`
- Create: `src/human_in_the_loop/review_queue.py`
- Create: `src/human_in_the_loop/approvals.py`
- Create: `src/human_in_the_loop/resume.py`
- Test: `tests/graph/test_human_review_timeout.py`

- [ ] Step 1: Write failing tests for:
  - timeout creates `safe_close_timeout` end reason
  - late normal resume rejected
  - force reopen creates new task with parent task id
  - review ticket creation is idempotent on duplicate interrupt
- [ ] Step 2: Implement watchdog contract (external timeout responsibility).
- [ ] Step 3: Implement approval actions and force_reopen behavior.
- [ ] Step 4: Ensure force_reopen creates new checkpoint chain under same `thread_id`.
- [ ] Step 5: Re-run tests.
Run: `pytest tests/graph/test_human_review_timeout.py -q`
Expected: pass.
- [ ] Step 6: Commit.

### Task 10: Persistence Backends and Replay Contracts

**Files:**
- Create: `src/persistence/checkpointers.py`
- Create: `src/persistence/stores.py`
- Create: `src/persistence/threads.py`
- Create: `src/persistence/replay.py`
- Create: `migrations/`
- Test: `tests/integration/test_persistence_runtime.py`

- [ ] Step 1: Write failing integration tests for thread/task/checkpoint persistence.
- [ ] Step 2: Implement dev sqlite / prod postgres policy checks.
- [ ] Step 3: Implement minimum DB schema for tasks, task_events, review_tickets, checkpoints, audit_events.
- [ ] Step 4: Implement PHI encryption-at-rest and redaction-safe persistence interfaces.
- [ ] Step 5: Implement checkpoint resume and replay metadata reads.
- [ ] Step 6: Re-run tests.
Run: `pytest tests/integration/test_persistence_runtime.py -q`
Expected: pass.
- [ ] Step 7: Commit.

### Task 11: Medical Consultation Graph and Core Nodes

**Files:**
- Create: `src/graphs/base.py`
- Create: `src/graphs/registry.py`
- Create: `src/graphs/versions.py`
- Create: `src/graphs/medical_consultation/graph.py`
- Create: `src/graphs/medical_consultation/nodes/intake.py`
- Create: `src/graphs/medical_consultation/nodes/triage_precheck.py`
- Create: `src/graphs/medical_consultation/nodes/clarify_intent.py`
- Create: `src/graphs/medical_consultation/nodes/human_review.py`
- Create: `src/graphs/medical_consultation/nodes/triage.py`
- Create: `src/graphs/medical_consultation/nodes/consultation.py`
- Create: `src/graphs/medical_consultation/nodes/diagnostic.py`
- Create: `src/graphs/medical_consultation/nodes/research.py`
- Create: `src/graphs/medical_consultation/nodes/synthesize.py`
- Create: `src/graphs/medical_consultation/nodes/safety_review.py`
- Create: `src/graphs/medical_consultation/nodes/final_response.py`
- Create: `src/graphs/medical_consultation/nodes/error_handler.py`
- Test: `tests/graph/test_medical_graph_runtime.py`

- [ ] Step 1: Write failing runtime graph test with mocked model/tool services.
- [ ] Step 2: Implement node patch outputs and graph compile wiring.
- [ ] Step 3: Enforce emergency non-delay behavior with static template logic.
- [ ] Step 4: Add explicit emergency assertions: no retrieval, no diagnostic, no research node execution.
- [ ] Step 5: Re-run graph tests.
Run: `pytest tests/graph/test_medical_graph_runtime.py -q`
Expected: pass.
- [ ] Step 6: Commit.

### Task 12: API and Worker Runtime

**Files:**
- Create: `apps/api/main.py`
- Create: `apps/api/deps.py`
- Create: `apps/api/schemas.py`
- Create: `apps/api/routes/tasks.py`
- Create: `apps/api/routes/threads.py`
- Create: `apps/api/routes/approvals.py`
- Create: `apps/worker/main.py`
- Create: `apps/worker/runner.py`
- Create: `apps/worker/lifecycle.py`
- Test: `tests/integration/test_api_worker_flow.py`

- [ ] Step 1: Write failing integration tests for async submit and polling flow.
- [ ] Step 2: Implement endpoints and worker loop.
- [ ] Step 3: Implement lease/heartbeat/max attempts behavior.
- [ ] Step 4: Re-run tests.
Run: `pytest tests/integration/test_api_worker_flow.py -q`
Expected: pass.
- [ ] Step 5: Commit.

### Task 13: Observability Layer

**Files:**
- Create: `src/observability/tracing.py`
- Create: `src/observability/logging.py`
- Create: `src/observability/metrics.py`
- Create: `src/observability/cost.py`
- Create: `src/observability/audit_log.py`
- Create: `src/observability/langsmith.py`
- Test: `tests/unit/test_observability_contracts.py`

- [ ] Step 1: Write failing tests for:
  - no raw PHI in traces
  - forbidden high-cardinality metric labels
- [ ] Step 2: Implement observability adapters.
- [ ] Step 3: Re-run tests.
Run: `pytest tests/unit/test_observability_contracts.py -q`
Expected: pass.
- [ ] Step 4: Commit.

### Task 14: Eval Runner and CI Gates

**Files:**
- Create: `src/evals/runner.py`
- Create: `src/evals/graders.py`
- Create: `src/evals/graph_regression.py`
- Create: `src/evals/tool_assertions.py`
- Create: `evals/datasets/`
- Create: `evals/golden/`
- Create: `evals/red_team/`
- Create: `evals/scenarios/`
- Test: `tests/evals/test_eval_gates.py`

- [ ] Step 1: Write failing eval-gate tests for zero emergency misses and zero high-severity leakage.
- [ ] Step 2: Implement eval runners and gate thresholds.
- [ ] Step 3: Re-run tests.
Run: `pytest tests/evals/test_eval_gates.py -q`
Expected: pass.
- [ ] Step 4: Commit.

### Task 15: End-to-End Verification and Release Readiness

**Files:**
- Modify: `README.md`
- Modify: `docs/operations.md` (create if missing)
- Test: full suite

- [ ] Step 1: Run full test suite.
Run: `pytest -q`
Expected: all pass.
- [ ] Step 2: Run architecture import smoke check.
Run: `python -c "from src.graphs.registry import get_graph; print('ok')"`
Expected: `ok`
- [ ] Step 3: Verify no contract divergence.
Run: manual checklist against `docs/langgraph-implementation-contract.md`
Expected: no mismatch.
- [ ] Step 4: Commit.

## Open Risk List (Must Be Watched During Execution)

1. Existing legacy modules use mixed encoding and hard-coded config paths.
2. Legacy tests depend on unavailable local dependencies in some environments.
3. Migration from current swarm runtime to LangGraph runtime must preserve safe fallback behavior.

## Execution Policy

1. No implementation starts until user confirms this plan.
2. TDD is mandatory per task.
3. Fresh verification evidence is mandatory before completion claims.
