from __future__ import annotations

from typing import Any, Callable


def require_llm_generate(services: dict[str, Any]) -> Callable[..., str]:
    fn = services.get("llm_generate")
    if not callable(fn):
        raise RuntimeError(
            "llm_generate service is required. This graph enforces LLM reasoning for all answers."
        )
    return fn


def call_llm(
    *,
    services: dict[str, Any],
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> str:
    llm_generate = require_llm_generate(services)
    text = llm_generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("llm_generate returned empty text.")
    return text.strip()
