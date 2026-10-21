# LangGraph Implementation Contract v1.1 (Agreed + Reviewed)

## Purpose

This file is the implementation contract for rewriting `medix-agent-swarm` into an industrial LangGraph system.
All coding must follow this contract. Any behavior change requires explicit approval and contract update first.

## Scope

- Project: `medix-agent-swarm`
- Orchestration: `LangGraph`
- Quality bar: reliability, safety, auditability, resumability, testability

## Non-Negotiable Architecture Rules

1. Hybrid typing model:
   - Graph runtime state: `TypedDict + Annotated reducers`
   - External boundaries (API/tools/contracts/results): `Pydantic`
2. Node functions return state patches only.
3. Routing is explicit, deterministic, and priority-ordered.
4. Safety policies are code-enforced (not prompt-only).
5. Human review is first-class (`interrupt`, queue, decision, timeout, resume/reopen).
6. All critical transitions emit trace/log/audit evidence.

## Canonical Node Names and Paths

The canonical high-risk reasoning path uses real node names only:

`triage -> diagnostic -> research -> synthesize -> safety_review -> final_response`

`diagnostic_research` is not a real node name in this contract.
If used at all, it is only a documentation alias for the chain above.

## Graph Edge Table (Canonical)

1. `intake -> triage_precheck`
2. `triage_precheck -> final_response` if `emergency_precheck_hit == true`
3. `triage_precheck -> clarify_intent` if `intent_status != resolved`
4. `triage_precheck -> consultation` if `intent_type == medical_info` and no `symptom_entities`
5. `triage_precheck -> triage` otherwise

6. `triage -> final_response` if `risk_level == emergency`
7. `triage -> consultation` if `risk_level in {low, medium}`
8. `triage -> diagnostic` if `risk_level == high`

9. `consultation -> final_response` if `next_action == finalize`
10. `consultation -> diagnostic` if `next_action == escalate_diagnostic`
11. `consultation -> clarify_intent` if `next_action == request_clarification`

12. `diagnostic -> research`
13. `research -> synthesize`
14. `synthesize -> safety_review`
15. `safety_review -> final_response` if safe
16. `safety_review -> human_review` if required by severity policy

17. `human_review -> triage` if `review_decision == approve_continue`
18. `human_review -> final_response` if `review_decision == safe_close`

## Intent and Clarification Contract

1. Intent must be resolved before non-emergency professional reasoning.
2. Thresholds:
   - `intent_confidence_resolved = 0.80`
   - `intent_confidence_ambiguous = 0.60`
3. `max_clarification_rounds = 3`
4. Clarification round counter increments for:
   - intent-gate clarification
   - consultation-driven clarification
5. If rounds reach max and still unresolved, route to `human_review`.

## Emergency Contract and Citation Exception

1. Once emergency is determined, response must not be delayed by runtime retrieval.
2. Emergency path uses pre-approved static emergency templates.
3. Emergency routing and wording are audit-cited to internal rule IDs.
4. Public emergency output may omit runtime citations.
5. Optional static trusted citations may be attached from preloaded safety sources.

## Triage Contract

1. Rule-first risk evaluation.
2. LLM refinement only for gray-zone risk.
3. High-risk emergency rule hit bypasses LLM and routes immediately.

## Consultation and Escalation Contract

1. `consultation` handles non-emergency `low/medium`.
2. Medium risk default posture is conservative (more likely to escalate).
3. `consultation` outputs `next_action` in:
   - `finalize`
   - `escalate_diagnostic`
   - `request_clarification`

## Diagnostic/Research/Synthesis Contract

1. `diagnostic`: differential analysis only, no definitive diagnosis, no dosage directives.
2. `research`: evidence retrieval/synthesis only with source metadata.
3. `synthesize`: if conflicts exist, default to more conservative/higher-risk guidance and annotate conflict notes.

## Safety Review Contract

Violation severity:

1. `high` -> immediate `human_review`
2. `medium` -> one auto-rewrite + recheck, then `human_review` if still failing
3. `low` -> warning and pass-through

High severity includes:

1. definitive diagnosis statements
2. specific medication dosage/frequency recommendations
3. emergency de-escalation language
4. medication advice for special populations (pregnancy/child/older adult)

## Citation Policy

Required citation classes:

1. medical claims
2. numeric thresholds
3. triage decisions

Citation optional:

1. generic advice
2. `safe_close` terminal responses

If required citation missing:

1. downgrade to evidence-insufficient wording
2. classify at least `medium` severity
3. escalate to human review if rewrite fails

Citation model constraints:

1. `published_date` optional
2. `excerpt <= 300 chars`
3. include `source_type`, `title`, `url or document_id`, `retrieved_at`, `evidence_quality`

`claim_citation_map` policy:

1. internal audit-only
2. not returned by default public API

## State Schema Contract (Minimum Required)

Minimum state keys include:

- `user_id`, `task_id`, `thread_id`, `trace_id`, `graph_name`, `graph_version`
- `raw_user_input`, `normalized_question`
- `intent_type`, `intent_confidence`, `intent_status`, `missing_required_slots`
- `clarification_rounds`, `clarification_history`
- `symptom_entities`, `emergency_precheck_hit`, `risk_level`
- `next_action`, `graph_status`, `end_reason`
- `diagnostic_result`, `research_evidence`, `synthesized_answer`
- `citations`, `safety_violations`, `audit_events`, `error_metadata`

## Reducer Strategy Contract

Overwrite keys:

- `risk_level`, `intent_status`, `next_action`, `graph_status`, `end_reason`

Append reducers:

- `messages`, `clarification_history`, `audit_events`, `trace_events`, `safety_violations`

Dedup reducers:

- `citations` (by `citation_id` or stable hash)
- `research_evidence` (by evidence ID/hash)

## Audit and Side-Effect Boundary

1. Nodes do not directly write audit DB records.
2. Nodes emit `audit_event` patches in state.
3. Runtime hooks/middleware persist audit events after node success/failure boundaries.
4. This is mandatory for unit-test isolation and deterministic replay.

## Human-in-the-Loop Timeout Contract

LangGraph `interrupt` pauses graph and waits indefinitely for resume unless externally handled.
Therefore timeout is enforced externally by worker/watchdog, not by interrupt itself.

Timeout process:

1. mark review ticket `timed_out`
2. append audit event
3. set task `end_reason = safe_close_timeout`
4. materialize `final_response` at runtime (worker/watchdog), not by continuing interrupted graph execution
5. close original task path

Late reviewer decision after timeout:

1. cannot resume original task
2. must use `force_reopen`

Human review ticket creation contract:

1. ticket creation must be idempotent by `(task_id, interrupt_point, reason)`
2. no non-idempotent side effects are allowed before `interrupt()`
3. if ticket already exists, reuse ticket ID and avoid duplicate queue insertion

## Task Lifecycle Contract

Statuses:

- `pending`, `claimed`, `running`, `interrupted`, `completed`, `failed`, `cancelled`

Transition table:

1. `pending -> claimed | cancelled`
2. `claimed -> running | failed | pending`
3. `running -> interrupted | completed | failed | cancelled`
4. `interrupted -> running | completed | failed | cancelled`
5. `completed -> terminal`
6. `failed -> terminal`
7. `cancelled -> terminal`

End reasons:

- `emergency`
- `safe_close_timeout`
- `safe_close_human`
- `normal_finalize`
- `cancelled_by_user`
- `failed_runtime`

Execution timeout:

- `execution_timeout_seconds = 120` for automated execution
- waiting in `interrupted` is excluded

Cancellation behavior:

1. `pending`: immediate cancel
2. `claimed/running`: set `cancellation_requested = true`, worker checks before each node/tool call
3. `interrupted`: cancel task and close review ticket
4. terminal states: reject cancellation

## Force Reopen Contract

1. Original timed-out task remains immutable terminal.
2. `force_reopen` creates a new task with:
   - `parent_task_id`
   - `reopen_reason`
3. Reopened task reuses original `thread_id`.
4. Reopened task creates a new checkpoint chain under same `thread_id` and new `task_id`.
5. Reopened execution starts from `triage`.

## API Contract (v1)

Public async flow:

1. `POST /tasks` -> `202 Accepted`
2. `GET /tasks/{task_id}`
3. `GET /tasks/{task_id}/result`
4. `POST /tasks/{task_id}/cancel`

HITL required APIs:

1. `POST /review-tickets/{ticket_id}/decision`
2. `POST /tasks/{task_id}/force-reopen`
3. `GET /review-tickets`
4. `GET /review-tickets/{ticket_id}`

No webhook in v1; polling only.

## Persistence and Recovery Contract

1. DB stack: `SQLAlchemy 2.x + Alembic`
2. Checkpointer backend:
   - dev default `sqlite`
   - prod required `postgres`
3. Prod startup fail-fast if:
   - missing `llm_api_key`
   - missing `db_url`
   - checkpointer backend not `postgres`
4. Crash recovery:
   - `claim_lease_seconds = 30`
   - `heartbeat_every_seconds = 10`
   - `max_retries = 2` (`max_total_attempts = 3`)
5. Reclaimed task resumes from latest durable checkpoint.
6. Reclaim emits audit event.
7. State migration failure:
   - set `error_code = state_migration_failed`
   - fail task safely

Minimum DB schema contract:

1. required tables:
   - `tasks`
   - `task_events`
   - `review_tickets`
   - `checkpoints`
   - `audit_events`
2. `tasks` minimum columns:
   - `task_id`, `parent_task_id`, `thread_id`, `user_id`
   - `graph_name`, `graph_version`, `status`, `end_reason`
   - `payload_encrypted`, `payload_hash`
   - `created_at`, `updated_at`
3. `review_tickets` minimum columns:
   - `ticket_id`, `task_id`, `thread_id`, `status`, `priority`
   - `reason`, `reviewer_id`, `expires_at`, `created_at`, `updated_at`

## Idempotency Contract

1. Key: `(user_id, graph_name, graph_version, payload_hash)`
2. Window: `60s`
3. Reuse only active task states:
   - `pending|claimed|running|interrupted`
4. Terminal match creates new task.

## Tool Runtime Contract

1. Tool interface is async-only.
2. Unified envelope: `ToolResult(status, data, error_code, error_message, meta)`
3. Permission denied returns `status = denied` (no exception)
4. Unknown tool:
   - `status = error`
   - `error_code = tool_not_found`
5. Timeout:
   - `status = timeout`
   - `error_code = tool_timeout`
6. Retry timeout once only:
   - base delay `300ms`
   - backoff factor `2.0`
   - max delay `2000ms`
   - jitter `+/-20%`

## PHI/PII Contract

1. Traces and metrics never contain raw PHI/PII.
2. Raw medical input in payload/checkpoint must be encrypted at rest.
3. Audit logs store minimum necessary context (redacted when possible).
4. Reviewer access to raw content is RBAC-protected and only through review UI/API.
5. Redaction policy must run before writing structured logs and review queue summaries.

## Observability Contract

1. Prod log level default: `INFO`
2. Metrics backend style: Prometheus
3. Forbidden high-cardinality metric labels:
   - `user_id`, `thread_id`, `task_id`
4. Use low-cardinality labels only (graph/node/status/tool)
5. Use trace/log for high-granularity debugging

## Evals and CI Gates

Blocking tolerances:

1. emergency miss tolerance = `0`
2. high-severity safety violation tolerance = `0`
3. if `intent_status != resolved`, diagnostic/research tool invocation must be `0`
4. emergency path must assert `no retrieval`, `no diagnostic`, `no research` node execution

Eval fixture families must include:

1. emergency symptom cases
2. ambiguous intent cases
3. high-risk non-emergency cases
4. dosage refusal cases
5. pregnancy/child/older adult cases
6. citation-missing cases
7. emergency de-escalation adversarial cases
8. routing regression snapshots

Medical evidence source policy:

Allowed by default:

1. government/public health authorities
2. recognized clinical guideline organizations
3. peer-reviewed medical literature
4. owner-approved institutional medical references

Disallowed by default:

1. forums
2. marketing pages
3. unverified blogs
4. SEO content without medical authority

## Config Priority Contract

Configuration order:

1. environment variables
2. `.env`
3. code defaults

## Implementation Order (Updated)

1. `src/config`
2. `src/contracts`
3. `src/graphs/medical_consultation/state.py`
4. `src/graphs/medical_consultation/routing.py`
5. routing regression tests
6. task lifecycle state machine tests
7. core nodes (`intake/triage/consultation/diagnostic/research/synthesize/safety_review/final_response`)
8. `src/tools` base + registry
9. `src/persistence`
10. HITL timeout watchdog + reopen flows
11. `src/guardrails`
12. `apps/api` + `apps/worker`
13. `src/observability`
14. `src/evals` + CI gates

## Change Control

No implementation may diverge from this contract unless:

1. user approves the behavior change, and
2. this file is updated first.
