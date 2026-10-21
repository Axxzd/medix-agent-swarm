from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["dev", "test", "staging", "prod"]
CheckpointBackend = Literal["sqlite", "postgres"]


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MEDIX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnv = "dev"
    log_level: str = "INFO"

    execution_timeout_seconds: int = 120
    human_review_timeout_seconds: int = 300
    max_clarification_rounds: int = 3

    intent_confidence_resolved: float = 0.80
    intent_confidence_ambiguous: float = 0.60

    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model_name: str = "gpt-4.1-mini"

    db_url: str | None = None
    checkpoint_backend: CheckpointBackend = "sqlite"

    enable_human_review: bool = True
    enable_langsmith_trace: bool = False
    langsmith_api_key: str | None = None

    @model_validator(mode="after")
    def validate_runtime_contract(self) -> "AppSettings":
        if self.app_env == "prod":
            missing: list[str] = []
            if not self.llm_api_key:
                missing.append("MEDIX_LLM_API_KEY")
            if not self.db_url:
                missing.append("MEDIX_DB_URL")
            if missing:
                raise ValueError(f"Missing required prod settings: {', '.join(missing)}")
            if self.checkpoint_backend != "postgres":
                raise ValueError("MEDIX_CHECKPOINT_BACKEND must be 'postgres' in prod.")
            if not self.enable_human_review:
                raise ValueError("MEDIX_ENABLE_HUMAN_REVIEW must be true in prod.")
        return self
