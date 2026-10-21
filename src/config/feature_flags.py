from __future__ import annotations

from dataclasses import dataclass

from .settings import AppSettings


@dataclass(frozen=True)
class FeatureFlags:
    enable_human_review: bool
    enable_research_node: bool
    enable_llm_triage_refine: bool
    enable_auto_rewrite_medium_violation: bool
    enable_langsmith_trace: bool


def build_feature_flags(settings: AppSettings) -> FeatureFlags:
    return FeatureFlags(
        enable_human_review=settings.enable_human_review,
        enable_research_node=True,
        enable_llm_triage_refine=True,
        enable_auto_rewrite_medium_violation=True,
        enable_langsmith_trace=settings.enable_langsmith_trace,
    )
