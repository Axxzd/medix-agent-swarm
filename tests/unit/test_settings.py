from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config.settings import AppSettings


def test_env_overrides_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MEDIX_LLM_MODEL_NAME=from_dotenv\n", encoding="utf-8")
    monkeypatch.setenv("MEDIX_LLM_MODEL_NAME", "from_env")

    settings = AppSettings(_env_file=env_file)

    assert settings.llm_model_name == "from_env"


def test_prod_requires_llm_api_key_and_db_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEDIX_APP_ENV", "prod")
    monkeypatch.delenv("MEDIX_LLM_API_KEY", raising=False)
    monkeypatch.delenv("MEDIX_DB_URL", raising=False)

    with pytest.raises(ValidationError):
        AppSettings(_env_file=None)


def test_prod_requires_postgres_checkpointer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEDIX_APP_ENV", "prod")
    monkeypatch.setenv("MEDIX_LLM_API_KEY", "k")
    monkeypatch.setenv("MEDIX_DB_URL", "postgresql+psycopg://u:p@localhost/db")
    monkeypatch.setenv("MEDIX_CHECKPOINT_BACKEND", "sqlite")

    with pytest.raises(ValidationError):
        AppSettings(_env_file=None)


def test_dev_defaults_are_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEDIX_APP_ENV", "dev")
    monkeypatch.delenv("MEDIX_LLM_API_KEY", raising=False)
    monkeypatch.delenv("MEDIX_DB_URL", raising=False)
    monkeypatch.delenv("MEDIX_CHECKPOINT_BACKEND", raising=False)

    settings = AppSettings(_env_file=None)

    assert settings.app_env == "dev"
    assert settings.checkpoint_backend == "sqlite"
