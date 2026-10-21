from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GraphVersionConfig:
    medical_consultation_default: str = "v1"


def get_graph_version_config() -> GraphVersionConfig:
    return GraphVersionConfig()
