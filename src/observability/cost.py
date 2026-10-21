from __future__ import annotations


def estimate_cost_usd(*, prompt_tokens: int, completion_tokens: int, price_per_1k: float) -> float:
    total_tokens = prompt_tokens + completion_tokens
    return round((total_tokens / 1000.0) * price_per_1k, 6)
