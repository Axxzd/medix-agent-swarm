# Industrial LangGraph Agentic Project Plan

## Goal

This document defines the target architecture for rewriting the current medical assistant project as an industrial-grade LangGraph agentic application.

The target system should be:

- Workflow-driven, not free-form agent-loop driven.
- Strongly typed at graph state, task, tool, and output boundaries.
- Recoverable through checkpoints and task lifecycle management.
- Auditable through structured traces, graph events, safety decisions, and final citations.
- Safe by construction, especially for medical triage, diagnosis, medication, privacy, and human escalation.
- Testable through unit tests, graph tests, integration tests, safety tests, and eval regression suites.

## Architecture Principles

1. Workflow owns orchestration.

   LangGraph graphs decide the execution path, branching, retry, checkpoint, interrupt, and finalization behavior.

2. Agents own reasoning.

   Agents are used inside graph nodes for bounded reasoning tasks. They do not decide the whole application lifecycle.

3. Tools own external actions.

   Tools perform retrieval, search, database access, filesystem access, browser access, and other side effects through typed contracts.

4. Guardrails own safety.

   Safety rules are implemented as code policies, permission checks, sandbox restrictions, and final output review. They are not only prompt instructions.

5. Persistence owns recovery.

   Task state, thread state, checkpoints, and replay data are first-class system concepts.

6. Observability owns diagnosis.

   Each graph run must emit trace IDs, node spans, tool calls, model usage, latency, cost, safety decisions, and final audit records.

7. Evals own quality gates.

   Regression cases, safety cases, and tool-call assertions are part of the release process.

## Target Project Structure

```text
langgraph-agentic-app/
├─ apps/
│  ├─ api/
│  │  ├─ main.py
│  │  ├─ deps.py
│  │  ├─ schemas.py
│  │  └─ routes/
│  │     ├─ tasks.py
│  │     ├─ threads.py
│  │     └─ approvals.py
│  ├─ worker/
│  │  ├─ main.py
│  │  ├─ runner.py
│  │  └─ lifecycle.py
│  └─ cli/
│     ├─ main.py
│     ├─ run.py
│     ├─ replay.py
│     └─ debug_node.py
│
├─ src/
│  ├─ graphs/
│  │  ├─ base.py
│  │  ├─ registry.py
│  │  ├─ versions.py
│  │  └─ medical_consultation/
│  │     ├─ graph.py
│  │     ├─ state.py
│  │     ├─ routing.py
│  │     └─ nodes/
│  │        ├─ intake.py
│  │        ├─ triage.py
│  │        ├─ retrieve.py
│  │        ├─ consultation.py
│  │        ├─ diagnostic.py
│  │        ├─ research.py
│  │        ├─ synthesize.py
│  │        ├─ safety_review.py
│  │        ├─ final_response.py
│  │        └─ error_handler.py
│  ├─ nodes/
│  │  └─ common/
│  │     ├─ model_call.py
│  │     ├─ tool_call.py
│  │     ├─ human_interrupt.py
│  │     └─ retry.py
│  ├─ state/
│  │  ├─ reducers.py
│  │  ├─ serializers.py
│  │  └─ migrations.py
│  ├─ contracts/
│  │  ├─ tasks.py
│  │  ├─ graph_events.py
│  │  ├─ tools.py
│  │  ├─ approvals.py
│  │  └─ outputs.py
│  ├─ tools/
│  │  ├─ base.py
│  │  ├─ registry.py
│  │  ├─ knowledge_search.py
│  │  ├─ guideline_search.py
│  │  ├─ risk_score.py
│  │  ├─ icd_lookup.py
│  │  └─ web_search.py
│  ├─ models/
│  │  ├─ client.py
│  │  ├─ providers.py
│  │  ├─ routing.py
│  │  └─ prompts.py
│  ├─ retrieval/
│  │  ├─ embeddings.py
│  │  ├─ vector_store.py
│  │  ├─ document_loader.py
│  │  ├─ chunking.py
│  │  ├─ reranker.py
│  │  └─ citations.py
│  ├─ persistence/
│  │  ├─ checkpointers.py
│  │  ├─ stores.py
│  │  ├─ threads.py
│  │  └─ replay.py
│  ├─ memory/
│  │  ├─ short_term.py
│  │  ├─ long_term.py
│  │  ├─ retrieval.py
│  │  └─ compaction.py
│  ├─ human_in_the_loop/
│  │  ├─ interrupts.py
│  │  ├─ approvals.py
│  │  ├─ review_queue.py
│  │  └─ resume.py
│  ├─ guardrails/
│  │  ├─ permissions.py
│  │  ├─ sandbox.py
│  │  ├─ medical_policy.py
│  │  ├─ output_policy.py
│  │  ├─ secrets.py
│  │  └─ audit.py
│  ├─ tasks/
│  │  ├─ model.py
│  │  ├─ store.py
│  │  ├─ claim.py
│  │  └─ lifecycle.py
│  ├─ workspaces/
│  │  ├─ manager.py
│  │  ├─ sandbox.py
│  │  ├─ locks.py
│  │  └─ cleanup.py
│  ├─ observability/
│  │  ├─ tracing.py
│  │  ├─ metrics.py
│  │  ├─ logging.py
│  │  ├─ langsmith.py
│  │  ├─ cost.py
│  │  └─ audit_log.py
│  ├─ evals/
│  │  ├─ runner.py
│  │  ├─ graders.py
│  │  ├─ graph_regression.py
│  │  └─ tool_assertions.py
│  └─ config/
│     ├─ settings.py
│     ├─ graph_versions.py
│     ├─ environments.py
│     └─ feature_flags.py
│
├─ prompts/
│  ├─ registry.yaml
│  └─ medical_consultation/
│     ├─ consultation.md
│     ├─ diagnostic.md
│     ├─ research.md
│     ├─ synthesize.md
│     └─ safety_review.md
├─ evals/
│  ├─ datasets/
│  ├─ golden/
│  ├─ red_team/
│  └─ scenarios/
├─ tests/
│  ├─ unit/
│  ├─ graph/
│  ├─ integration/
│  ├─ safety/
│  └─ fixtures/
├─ docs/
├─ migrations/
├─ scripts/
├─ pyproject.toml
├─ .env.example
└─ README.md
```

## Python File Responsibilities

### `apps/api`

| File | Responsibility |
| --- | --- |
| `apps/api/main.py` | FastAPI application entrypoint. Creates the app, registers routers, configures middleware, initializes lifecycle hooks, and exposes health checks. |
| `apps/api/deps.py` | API dependency injection. Provides settings, task store, graph registry, approval service, and authenticated request context to route handlers. |
| `apps/api/schemas.py` | API-facing request and response schemas. Keeps HTTP contracts separate from internal graph state. |
| `apps/api/routes/tasks.py` | Task APIs. Creates graph tasks, queries task status, returns final results, and cancels running tasks. |
| `apps/api/routes/threads.py` | Thread and checkpoint APIs. Lists thread history, graph checkpoints, replay metadata, and execution events. |
| `apps/api/routes/approvals.py` | Human approval APIs. Submits approval decisions, rejects unsafe actions, and resumes interrupted graph executions. |

### `apps/worker`

| File | Responsibility |
| --- | --- |
| `apps/worker/main.py` | Worker process entrypoint. Loads configuration, initializes dependencies, and starts the worker runtime. |
| `apps/worker/runner.py` | Task runner. Claims queued tasks, resolves graph version, invokes the compiled LangGraph graph, persists results, and handles graph-level failures. |
| `apps/worker/lifecycle.py` | Worker lifecycle management. Handles startup, shutdown, heartbeat, lease renewal, and graceful cancellation. |

### `apps/cli`

| File | Responsibility |
| --- | --- |
| `apps/cli/main.py` | CLI entrypoint. Registers local commands for graph execution, replay, and node debugging. |
| `apps/cli/run.py` | Local graph runner. Executes a selected graph from a local payload without the API or worker queue. |
| `apps/cli/replay.py` | Checkpoint replay command. Reconstructs graph state from persisted checkpoints and replays execution for debugging. |
| `apps/cli/debug_node.py` | Single-node debugger. Runs one node with a supplied state fixture and prints the resulting state patch. |

### `src/graphs`

| File | Responsibility |
| --- | --- |
| `src/graphs/base.py` | Shared graph factory utilities. Applies dependency injection, checkpointer wiring, graph configuration, and compile options. |
| `src/graphs/registry.py` | Graph registry. Maps graph name and version to compiled graph definitions and exposes lookup APIs. |
| `src/graphs/versions.py` | Graph version metadata. Defines supported graph versions, compatibility rules, and deprecation policy. |

### `src/graphs/medical_consultation`

| File | Responsibility |
| --- | --- |
| `src/graphs/medical_consultation/graph.py` | Medical consultation `StateGraph` definition. Adds nodes, conditional edges, error paths, interrupt points, and final compile step. |
| `src/graphs/medical_consultation/state.py` | Medical consultation state schema. Defines typed fields such as question, patient context, risk level, route, evidence, node outputs, safety findings, citations, and final answer. |
| `src/graphs/medical_consultation/routing.py` | Medical consultation routing functions. Decides whether to enter emergency response, normal consultation, complex diagnostic analysis, research, safety review, or termination. |
| `src/graphs/medical_consultation/nodes/intake.py` | Intake node. Normalizes user input, validates required context, extracts patient profile fields, and initializes graph metadata. |
| `src/graphs/medical_consultation/nodes/triage.py` | Triage node. Detects emergency symptoms, assigns risk level, and determines whether the graph must force emergency guidance. |
| `src/graphs/medical_consultation/nodes/retrieve.py` | Retrieval node. Fetches relevant knowledge, guidelines, prior thread memory, and long-term memory snippets. |
| `src/graphs/medical_consultation/nodes/consultation.py` | Consultation reasoning node. Produces general health guidance for non-emergency, low-to-medium risk questions. |
| `src/graphs/medical_consultation/nodes/diagnostic.py` | Diagnostic reasoning node. Analyzes symptom patterns and differential possibilities without making a definitive diagnosis. |
| `src/graphs/medical_consultation/nodes/research.py` | Evidence research node. Summarizes retrieved guidelines and external evidence into citation-ready findings. |
| `src/graphs/medical_consultation/nodes/synthesize.py` | Synthesis node. Merges consultation, diagnostic, and research outputs into a candidate final response. |
| `src/graphs/medical_consultation/nodes/safety_review.py` | Safety review node. Applies medical, privacy, medication, diagnosis, and citation policies before final output. |
| `src/graphs/medical_consultation/nodes/final_response.py` | Final response node. Produces the user-facing answer, citations, disclaimer, follow-up suggestions, and audit summary. |
| `src/graphs/medical_consultation/nodes/error_handler.py` | Error handling node. Converts recoverable graph errors into safe user-facing responses and records failure metadata. |

### `src/nodes/common`

| File | Responsibility |
| --- | --- |
| `src/nodes/common/model_call.py` | Common model-call node helper. Wraps LLM invocation with tracing, timeout, retry, schema parsing, and cost accounting. |
| `src/nodes/common/tool_call.py` | Common tool-call node helper. Enforces tool permissions, validates tool input/output schemas, and records tool audit events. |
| `src/nodes/common/human_interrupt.py` | Common interrupt helper. Creates LangGraph interrupts for approval, review, or clarification workflows. |
| `src/nodes/common/retry.py` | Common retry and fallback helper. Applies bounded retries, records retry causes, and emits fallback state patches. |

### `src/state`

| File | Responsibility |
| --- | --- |
| `src/state/reducers.py` | Shared LangGraph state reducers. Defines append, merge, deduplicate, and last-write-wins behavior for common state fields. |
| `src/state/serializers.py` | State serialization. Converts graph state to and from persistence-safe formats. |
| `src/state/migrations.py` | State schema migrations. Upgrades old checkpoint payloads to current state versions. |

### `src/contracts`

| File | Responsibility |
| --- | --- |
| `src/contracts/tasks.py` | Task contracts. Defines task creation payloads, status models, result models, and cancellation models. |
| `src/contracts/graph_events.py` | Graph event contracts. Defines node started, node completed, tool called, model called, interrupted, resumed, failed, and completed events. |
| `src/contracts/tools.py` | Tool contracts. Defines base input/output models, permission metadata, failure models, and typed tool result wrappers. |
| `src/contracts/approvals.py` | Approval contracts. Defines approval request, approval decision, reviewer metadata, and resume payloads. |
| `src/contracts/outputs.py` | Output contracts. Defines final answer, citation, disclaimer, safety warning, and structured response schemas. |

### `src/tools`

| File | Responsibility |
| --- | --- |
| `src/tools/base.py` | Tool protocol and metadata. Defines common call interface, input schema, output schema, timeout, side-effect level, and required permissions. |
| `src/tools/registry.py` | Tool registry. Registers tools, resolves tools by name/version, and checks whether a graph node may use them. |
| `src/tools/knowledge_search.py` | Medical knowledge search tool. Queries the curated knowledge base and returns ranked evidence snippets. |
| `src/tools/guideline_search.py` | Clinical guideline search tool. Retrieves guideline passages with source metadata and freshness information. |
| `src/tools/risk_score.py` | Risk scoring tool. Applies deterministic symptom rules and optional model-assisted classification for triage. |
| `src/tools/icd_lookup.py` | ICD lookup tool. Finds ICD codes and disease classification metadata when needed for explanation or coding support. |
| `src/tools/web_search.py` | External search tool. Performs controlled web or literature search with source filtering, timeout, and citation metadata. |

### `src/models`

| File | Responsibility |
| --- | --- |
| `src/models/client.py` | Unified model client interface. Provides chat, structured output, embeddings, streaming, and cancellation-friendly APIs. |
| `src/models/providers.py` | Provider adapters. Implements OpenAI-compatible, local, or other model provider clients behind the shared interface. |
| `src/models/routing.py` | Model routing. Chooses model by task type, risk level, cost budget, latency target, and fallback policy. |
| `src/models/prompts.py` | Prompt loading. Loads prompt templates from `prompts/`, injects variables, validates prompt versions, and binds output schemas. |

### `src/retrieval`

| File | Responsibility |
| --- | --- |
| `src/retrieval/embeddings.py` | Embedding model wrapper. Generates embeddings with batching, caching, and provider abstraction. |
| `src/retrieval/vector_store.py` | Vector store adapter. Encapsulates Milvus, Qdrant, or local vector store operations. |
| `src/retrieval/document_loader.py` | Document loader. Reads source documents, extracts metadata, and prepares ingestion records. |
| `src/retrieval/chunking.py` | Chunking strategy. Splits documents into retrieval-safe chunks with overlap and metadata propagation. |
| `src/retrieval/reranker.py` | Reranking logic. Reorders retrieved chunks using heuristic or model-based ranking. |
| `src/retrieval/citations.py` | Citation builder. Converts retrieved evidence into stable citation objects for final answers and audit logs. |

### `src/persistence`

| File | Responsibility |
| --- | --- |
| `src/persistence/checkpointers.py` | LangGraph checkpointer configuration. Provides memory, SQLite, Postgres, or Redis-backed checkpoint implementations. |
| `src/persistence/stores.py` | Storage adapters. Persists tasks, graph events, thread state, memory records, and audit data. |
| `src/persistence/threads.py` | Thread management. Creates thread IDs, maps user sessions to threads, and lists checkpoint history. |
| `src/persistence/replay.py` | Replay service. Reconstructs graph runs from checkpoints and events for debugging and incident analysis. |

### `src/memory`

| File | Responsibility |
| --- | --- |
| `src/memory/short_term.py` | Short-term memory. Stores thread-level recent messages and graph-local context. |
| `src/memory/long_term.py` | Long-term memory. Stores cross-session summaries and user-level durable facts when permitted. |
| `src/memory/retrieval.py` | Memory retrieval. Searches short-term and long-term memory with filtering and permission checks. |
| `src/memory/compaction.py` | Memory compaction. Summarizes, deduplicates, expires, and compresses memory records. |

### `src/human_in_the_loop`

| File | Responsibility |
| --- | --- |
| `src/human_in_the_loop/interrupts.py` | Interrupt definitions. Defines when graph execution pauses for approval, clarification, or safety review. |
| `src/human_in_the_loop/approvals.py` | Approval service. Applies approval rules, validates reviewer decisions, and writes approval events. |
| `src/human_in_the_loop/review_queue.py` | Review queue. Stores pending human review items and supports assignment, claiming, and timeout handling. |
| `src/human_in_the_loop/resume.py` | Resume service. Converts approval decisions into graph resume commands and state patches. |

### `src/guardrails`

| File | Responsibility |
| --- | --- |
| `src/guardrails/permissions.py` | Permission policy. Decides whether a graph, node, agent, or user may call a tool or perform an action. |
| `src/guardrails/sandbox.py` | Runtime sandbox. Restricts filesystem, network, shell command, and workspace access. |
| `src/guardrails/medical_policy.py` | Medical policy. Enforces emergency escalation, no definitive diagnosis, medication boundaries, and uncertainty handling. |
| `src/guardrails/output_policy.py` | Output policy. Checks final response format, disclaimers, citations, refusal language, and safe wording. |
| `src/guardrails/secrets.py` | Secret scanning. Detects API keys, tokens, credentials, and private data in inputs, outputs, and tool payloads. |
| `src/guardrails/audit.py` | Guardrail audit. Records denied actions, safety warnings, policy decisions, and reviewer overrides. |

### `src/tasks`

| File | Responsibility |
| --- | --- |
| `src/tasks/model.py` | Task domain model. Defines task identity, graph target, status, priority, thread ID, user ID, timestamps, and result references. |
| `src/tasks/store.py` | Task store interface. Creates, updates, queries, and persists tasks independent of graph state. |
| `src/tasks/claim.py` | Task claiming. Lets workers claim tasks, renew leases, release tasks, and avoid duplicate execution. |
| `src/tasks/lifecycle.py` | Task lifecycle. Centralizes transitions such as pending, running, paused, failed, cancelled, and completed. |

### `src/workspaces`

| File | Responsibility |
| --- | --- |
| `src/workspaces/manager.py` | Workspace manager. Creates isolated workspace directories and maps tasks to workspaces. |
| `src/workspaces/sandbox.py` | Workspace sandbox. Enforces file access and command execution rules inside a workspace. |
| `src/workspaces/locks.py` | Workspace locks. Prevents concurrent tasks from modifying the same isolated resources. |
| `src/workspaces/cleanup.py` | Workspace cleanup. Removes expired temporary files, stale locks, and old workspaces. |

### `src/observability`

| File | Responsibility |
| --- | --- |
| `src/observability/tracing.py` | Tracing. Creates trace IDs, node spans, tool spans, model spans, and graph-level traces. |
| `src/observability/metrics.py` | Metrics. Records latency, success rate, failure rate, tool error rate, queue time, and safety violation count. |
| `src/observability/logging.py` | Structured logging. Configures JSON logs and injects task ID, thread ID, trace ID, graph name, and node name. |
| `src/observability/langsmith.py` | LangSmith integration. Sends LangGraph and LLM traces to LangSmith when enabled. |
| `src/observability/cost.py` | Cost tracking. Aggregates model token cost, tool cost, and graph-run cost by task and user. |
| `src/observability/audit_log.py` | User-visible audit log. Stores key graph actions, safety decisions, citations, and final response metadata. |

### `src/evals`

| File | Responsibility |
| --- | --- |
| `src/evals/runner.py` | Eval runner. Executes eval datasets against graph versions and writes score reports. |
| `src/evals/graders.py` | Graders. Scores answer quality, safety behavior, citation quality, and task completion. |
| `src/evals/graph_regression.py` | Graph regression checks. Compares graph paths, node outputs, safety decisions, and final responses against golden cases. |
| `src/evals/tool_assertions.py` | Tool assertions. Verifies required tools were used, forbidden tools were not used, and tool inputs were valid. |

### `src/config`

| File | Responsibility |
| --- | --- |
| `src/config/settings.py` | Runtime settings. Loads environment variables through `pydantic-settings` and exposes typed config. |
| `src/config/graph_versions.py` | Graph version settings. Defines default graph versions, rollout percentages, and version pinning. |
| `src/config/environments.py` | Environment profiles. Encodes dev, test, staging, and production differences. |
| `src/config/feature_flags.py` | Feature flags. Enables staged rollout of graph nodes, tools, models, and guardrail behaviors. |

## Non-Python Project Areas

| Path | Responsibility |
| --- | --- |
| `prompts/registry.yaml` | Prompt registry with prompt IDs, versions, target nodes, owners, and expected output schemas. |
| `prompts/medical_consultation/*.md` | Prompt templates for medical consultation graph nodes. |
| `evals/datasets/` | Raw eval datasets. |
| `evals/golden/` | Golden cases for regression testing. |
| `evals/red_team/` | High-risk adversarial and safety cases. |
| `evals/scenarios/` | Scenario definitions for multi-step graph evaluation. |
| `tests/unit/` | Unit tests for pure functions, policies, schemas, tools, and reducers. |
| `tests/graph/` | Graph execution tests with mocked model and tool dependencies. |
| `tests/integration/` | Integration tests for persistence, retrieval, memory, and external adapters. |
| `tests/safety/` | Safety tests for emergency escalation, diagnosis boundaries, medication boundaries, and privacy leakage. |
| `tests/fixtures/` | Shared test payloads, checkpoint samples, model responses, and tool outputs. |
| `docs/` | Architecture, graph design, state schema, tool contracts, HITL, persistence, evals, and operations documentation. |
| `migrations/` | Database and state-store migrations. |
| `scripts/` | Offline commands for indexing documents, running evals, smoke testing deployments, and maintenance. |

## Medical Consultation Graph Flow

```text
START
  -> intake
  -> triage
  -> route_after_triage

if emergency:
  -> final_response
  -> END

if normal_consultation:
  -> retrieve
  -> consultation
  -> safety_review
  -> final_response
  -> END

if complex_symptoms:
  -> retrieve
  -> diagnostic
  -> research
  -> synthesize
  -> safety_review
  -> final_response
  -> END

if retrieval_or_model_failure:
  -> error_handler
  -> safety_review
  -> final_response
  -> END
```

## Minimum Viable Industrial Slice

The first implementation slice should not create every graph and every app. It should prove the industrial runtime path with one graph.

Build first:

1. `apps/api`
2. `apps/worker`
3. `src/graphs/medical_consultation`
4. `src/tools`
5. `src/persistence`
6. `src/guardrails`
7. `src/observability`
8. `tests/graph`
9. `tests/safety`

Defer until the first graph is stable:

1. `apps/web`
2. Multiple business graphs
3. Advanced workspace isolation
4. Full LangSmith dashboards
5. Large-scale eval automation

## Acceptance Criteria

The rewrite should be considered production-ready only when these criteria are met:

1. A user can submit a task through the API and receive a task ID.
2. A worker can claim the task, run the graph, checkpoint state, and persist a final result.
3. The graph can be resumed from a checkpoint after interruption.
4. Emergency medical symptoms force safe escalation behavior.
5. Medication dosage and definitive diagnosis requests are blocked or rewritten safely.
6. Final medical answers include uncertainty language, citations when evidence is used, and a disclaimer.
7. Every model call, tool call, node transition, and safety decision is traceable by `trace_id`.
8. Unit, graph, integration, safety, and eval tests can run in CI.
9. The system can run locally from documented commands using `.env.example`.
10. Prompt versions, graph versions, and state schema versions are explicit and auditable.
