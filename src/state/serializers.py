from __future__ import annotations

import json
from typing import Any, Mapping


def serialize_state(state: Mapping[str, Any]) -> dict[str, Any]:
    # Round-trip through JSON-compatible value transformation to reject
    # unserializable objects before persistence boundaries.
    normalized = json.loads(json.dumps(state, ensure_ascii=False, default=str))
    return dict(normalized)


def deserialize_state(payload: Mapping[str, Any]) -> dict[str, Any]:
    return dict(payload)
