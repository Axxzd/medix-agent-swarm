# Security policy

This project is a local development prototype. No production security support or clinical safety certification is claimed.

## Reporting a vulnerability

Use the repository's **Security → Advisories → Report a vulnerability** feature if the maintainer has enabled private vulnerability reporting. If that option is absent, use a private contact listed in the maintainer's GitHub profile. If no private route is available, open an issue asking for a reporting contact without disclosing exploit details or sensitive data.

Include affected files, reproduction steps with synthetic inputs, expected impact and any suggested mitigation. No response-time guarantee is currently offered.

## Known deployment limits

- The API has no authentication, authorization or tenant isolation; keep it bound to localhost.
- Task storage is in-memory in the development stack.
- Demonstration evidence and software policy checks are not clinically validated safeguards.
- Local SQLite encoding helpers must not be relied on as production cryptography.
- Never expose credentials or real patient information in issues, logs, examples or test artifacts.

Before publishing, scan the files being committed and their Git history for secrets. Removing a leaked key from a file does not revoke it; revoke or rotate it at the issuing provider.
