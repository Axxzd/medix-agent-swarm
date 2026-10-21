from __future__ import annotations

import re


def redact_secrets(text: str) -> str:
    redacted = text
    redacted = re.sub(r"(sk-[A-Za-z0-9_\-]{8,})", "[REDACTED_KEY]", redacted)
    redacted = re.sub(
        r"(api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{6,})",
        "api_key=[REDACTED]",
        redacted,
        flags=re.IGNORECASE,
    )
    return redacted
