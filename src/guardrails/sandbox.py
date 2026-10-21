from __future__ import annotations

from pathlib import Path


def is_path_within_workspace(path: str, workspace_root: str) -> bool:
    target = Path(path).resolve()
    root = Path(workspace_root).resolve()
    return root == target or root in target.parents
