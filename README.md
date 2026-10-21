# medix-agent-swarm

A Python research prototype for medical consultation workflows: explicit graph routing, structured task contracts, an API/worker loop, human-review lifecycle primitives, and regression tests.

中文说明：[README.zh-CN.md](README.zh-CN.md).

**Status: development prototype.** This project is for software research and education. It has no demonstrated clinical validation and must not be used for diagnosis, treatment, or emergency decisions. Use synthetic inputs for demos and issues.

## What is implemented

- A custom `GraphApp` executor with intake, triage, clarification, consultation, research, synthesis, safety-review and final-response nodes.
- FastAPI endpoints for tasks, threads and approval decisions, with an in-memory task store and worker retry/lease handling.
- Pydantic contracts for tasks, outputs, citations, tools and review tickets.
- Separate SQLite storage, checkpoint/replay helpers and human-review timeout/resume components, with tests.
- Tests for graph routing, task lifecycle, API/worker integration, output policies and evaluation gates. Model calls are replaced with deterministic test doubles in tests.

## Current limits

- The graph executor is custom Python; the LangGraph documents under `docs/` describe a design direction, not a completed LangGraph SDK integration.
- The default research node returns demonstration evidence. The graph supports an injected retriever, but the development worker does not configure a real evidence source. Default citations must not be represented as verified medical references.
- API and worker share an in-memory store in one process. Restart loses API tasks. The separate SQLite helpers are not wired into this API runtime; a PostgreSQL backend is not implemented.
- Human-review lifecycle components are tested separately. The graph's human-review node defaults to safe close; it does not implement a complete pause-and-resume clinical review workflow.
- The API has no authentication or tenant access control. Bind it to localhost for development.
- Passing software tests establishes only the tested software behavior, not medical accuracy, clinical safety, real adoption or production readiness.

## Quick start

Use Python 3.12. From this directory:

```sh
python -m venv .venv
# Activate: Windows PowerShell: .venv\Scripts\Activate.ps1
# Activate: Linux/macOS: . .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell; `cp .env.example .env` in a POSIX shell). Set `MEDIX_LLM_API_KEY` locally and choose a model your provider makes available. The default base URL uses OpenAI; a different provider requires its corresponding `MEDIX_LLM_BASE_URL` and model name. Live requests use your provider credentials and may incur charges. Tests do not require a real API key.

```sh
python scripts/run_dev_stack.py --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/docs>. In another terminal with the same environment:

```sh
python scripts/run_terminal_chat.py --api-base-url http://127.0.0.1:8000
```

The combined dev stack is required: launching API and worker separately does not share the in-memory runtime. See [RUNBOOK](docs/RUNBOOK.md) for API examples.

## Verification

```sh
python -m pytest -q
```

The initial audit found two legacy tests referring to absent `swarm` and `knowledge.milvus_kb` modules. Their original source is preserved in [archive/legacy-tests](archive/legacy-tests/README.md). See [verification notes](docs/VERIFICATION.md) for observed local results and their limits. The GitHub Actions workflow runs the entire active `tests/` suite; see the actual [CI runs](https://github.com/Axxzd/medix-agent-swarm/actions/workflows/tests.yml) for hosted results.

## Layout

| Path | Purpose |
| --- | --- |
| `apps/api`, `apps/worker` | Local task API and worker |
| `src/graphs`, `src/state` | Custom graph executor, nodes and state reducers |
| `src/contracts`, `src/tools` | Typed contracts and tool registry |
| `src/persistence` | Separate SQLite checkpoint/replay helpers |
| `src/human_in_the_loop` | Review tickets, timeout and resume components |
| `src/guardrails`, `src/observability` | Policy helpers and tracing contracts |
| `tests` | Software regression tests |
| `docs` | Runbook, verification notes and architecture proposals |

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Report reproducible bugs and contribute focused changes with tests. Do not submit real patient information or credentials.

License: [MIT](LICENSE). Third-party dependencies retain their own licenses. The MIT grant covers only code the contributors have the right to license; no external medical datasets or model weights are included or licensed here.
