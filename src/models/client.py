from __future__ import annotations

from typing import Callable

from openai import OpenAI

from src.config.settings import AppSettings


def build_llm_generate_from_settings(
    settings: AppSettings,
) -> Callable[..., str]:
    if not settings.llm_api_key:
        raise RuntimeError(
            "MEDIX_LLM_API_KEY is required. All responses must use LLM reasoning."
        )

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    model_name = settings.llm_model_name

    def llm_generate(
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        response = client.chat.completions.create(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned empty content.")
        return str(content).strip()

    return llm_generate
