from __future__ import annotations

from .settings import AppEnv, AppSettings


def is_prod(settings: AppSettings) -> bool:
    return settings.app_env == "prod"


def is_non_prod(settings: AppSettings) -> bool:
    return settings.app_env in {"dev", "test", "staging"}
