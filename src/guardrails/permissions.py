from __future__ import annotations


def is_tool_allowed(tool_name: str, allowed_tools: set[str] | None) -> bool:
    if allowed_tools is None:
        return True
    return tool_name in allowed_tools
