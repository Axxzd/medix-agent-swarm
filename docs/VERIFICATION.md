# Verification record

Audit date: 2026-10-21. This records local software verification, not clinical validation or GitHub Actions results.

## Baseline

The supplied directory had no README, dependency manifest, license or Git repository. Its runbook reported a historical `54 passed`; that was not accepted as a fresh result.

The initial full-suite command `python -m pytest -q -p no:cacheprovider` stopped during collection because `knowledge.milvus_kb` was absent. Another legacy test referenced the absent `swarm` module. Both original files are retained unchanged as text in `archive/legacy-tests/`; the archive README explains how to restore them when their implementation is available.

## Current implementation

Environment: Windows, Python 3.12.12, FastAPI 0.135.1, Pydantic 2.12.5, pydantic-settings 2.14.0, httpx 0.27.0, OpenAI Python SDK 1.109.1, uvicorn 0.42.0, pytest 9.0.2.

The current implementation was checked with:

```sh
python -m pytest tests/unit tests/graph tests/integration tests/safety tests/evals -q -p no:cacheprovider --basetemp=.test-tmp-oss-a83e107c
```

Observed result: **55 passed, 73 warnings**. All warnings in that run were `datetime.utcnow()` deprecation warnings. A dedicated fresh temporary directory was used because this machine's default pytest temporary parent returned `PermissionError`.

After archiving the legacy test source, default discovery was checked with:

```sh
python -m pytest -q -p no:cacheprovider --basetemp=.test-tmp-final-319ccf42 --disable-warnings
```

Observed result: **55 passed, 73 warnings**. The command discovered all active tests without a directory or file selection. `--disable-warnings` abbreviated the report; warnings were still counted, not treated as errors or removed.

A fresh project-local `.venv` was created with Python 3.12 and populated using `python -m pip install -r requirements-dev.txt`. Its checks were:

```sh
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.test-tmp-clean-a26f3b85 --disable-warnings
```

Observed results: **No broken requirements found**; **55 passed, 74 warnings**. This verifies installation and all active tests without relying on the existing Conda environment's extra packages. Transitive dependency versions were resolved by pip during this install; the requirements files pin direct dependencies, not a complete transitive lock.

The clean environment reported deprecation warnings; they have not been fixed in this publication-preparation change. The original repository-wide whitespace check also found existing Markdown hard breaks and extra terminal blank lines. Markdown hard breaks were rewritten with equivalent CommonMark backslashes, and terminal blank lines were normalized, without changing application behavior.

## Scope of evidence

- Model calls in the suite use test doubles. No live model-quality or medical-accuracy measurement was performed.
- Passing the SQLite helper tests does not demonstrate durable persistence in the API worker runtime.
- Passing human-review component tests does not demonstrate an end-to-end pause/resume clinical review workflow.
- The cross-platform GitHub Actions workflow runs the full active suite on Linux and Windows. Hosted results must be checked in the repository's [actual CI runs](https://github.com/Axxzd/medix-agent-swarm/actions/workflows/tests.yml), separately from the local results in this record.
- This local verification does not establish user adoption, downloads, ecosystem impact or an external deployment.
- `.env.example` contained a credential-shaped value and was sanitized. Local `.env` is excluded by `.gitignore`. Any potentially exposed key must still be revoked or rotated by its owner.
