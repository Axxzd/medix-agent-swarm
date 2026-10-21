# Contributing

This is a development prototype. Read the implementation limits in the README before proposing changes. Start with a reproducible issue or a focused pull request; describe the problem, observed behavior and expected behavior.

## Development

Use Python 3.12 and install `requirements-dev.txt` in a virtual environment. Run `python -m pytest -q` before submitting a change. See `docs/VERIFICATION.md` for the baseline and legacy-test archive; report failures rather than silently excluding tests.

Tests should use synthetic inputs and deterministic model/tool doubles. Do not require personal API keys, network access or patient records. Changes to routing, task states, retries, timeout/resume or output contracts should include a regression test for the affected behavior.

## Pull requests

- Explain the resulting behavior and any limits in plain language.
- Include the exact verification command and its result.
- Keep unrelated refactors out of the change.
- Update documentation when behavior or setup changes.
- Distinguish design proposals from features actually implemented.

Only contribute code and content you have the right to license under the project MIT license. Preserve third-party notices. Do not add copied proprietary material or external datasets without explicit redistribution rights and attribution.

## Sensitive information

Never include API keys, `.env` files, real medical records or identifiable chat logs. Use the private reporting route in `SECURITY.md` for vulnerabilities.
