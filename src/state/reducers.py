from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


def _normalize_item(item: Mapping[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def _stable_hash(item: Mapping[str, Any]) -> str:
    return hashlib.sha256(_normalize_item(item).encode("utf-8")).hexdigest()


def append_items(
    current: list[dict[str, Any]] | None,
    incoming: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    left = list(current or [])
    right = list(incoming or [])
    return [*left, *right]


def _citation_key(item: Mapping[str, Any]) -> str:
    citation_id = item.get("citation_id")
    if citation_id:
        return f"citation_id:{citation_id}"

    source_id = item.get("source_id")
    locator = item.get("locator")
    if source_id and locator:
        return f"source_locator:{source_id}:{locator}"
    return f"hash:{_stable_hash(item)}"


def merge_citations(
    current: list[dict[str, Any]] | None,
    incoming: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _iter_items(current, incoming):
        key = _citation_key(item)
        if key in seen:
            continue
        seen.add(key)
        merged.append(dict(item))
    return merged


def _evidence_key(item: Mapping[str, Any]) -> str:
    evidence_id = item.get("evidence_id")
    if evidence_id:
        return f"evidence_id:{evidence_id}"
    return f"hash:{_stable_hash(item)}"


def merge_evidence(
    current: list[dict[str, Any]] | None,
    incoming: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _iter_items(current, incoming):
        key = _evidence_key(item)
        if key in seen:
            continue
        seen.add(key)
        merged.append(dict(item))
    return merged


def _iter_items(
    current: Iterable[Mapping[str, Any]] | None,
    incoming: Iterable[Mapping[str, Any]] | None,
) -> Iterable[Mapping[str, Any]]:
    for item in current or []:
        yield item
    for item in incoming or []:
        yield item
