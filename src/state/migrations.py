from __future__ import annotations

from typing import Any, Callable

StateDict = dict[str, Any]
MigrationFn = Callable[[StateDict], StateDict]


class MigrationError(RuntimeError):
    pass


_MIGRATIONS: dict[tuple[str, str], MigrationFn] = {}


def register_migration(from_version: str, to_version: str, fn: MigrationFn) -> None:
    _MIGRATIONS[(from_version, to_version)] = fn


def migrate_state(state: StateDict, from_version: str, to_version: str) -> StateDict:
    if from_version == to_version:
        return dict(state)

    key = (from_version, to_version)
    migration = _MIGRATIONS.get(key)
    if migration is None:
        raise MigrationError(
            f"No state migration registered from '{from_version}' to '{to_version}'."
        )
    migrated = migration(dict(state))
    migrated["graph_version"] = to_version
    return migrated
