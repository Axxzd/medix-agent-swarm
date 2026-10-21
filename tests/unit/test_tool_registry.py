from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contracts.tools import ToolResultStatus
from src.tools.base import BaseTool
from src.tools.registry import ToolRegistry


class EchoTool(BaseTool):
    name = "echo"

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"echo": payload}


class SlowTool(BaseTool):
    name = "slow"

    def __init__(self) -> None:
        self.attempts = 0

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.attempts += 1
        await asyncio.sleep(0.03)
        return {"done": True}


def test_tool_registry_denied_returns_denied_status() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())
    result = asyncio.run(registry.call("echo", {"x": 1}, allowed_tools=set()))
    assert result.status == ToolResultStatus.denied
    assert result.error_code == "permission_denied"


def test_tool_registry_unknown_tool_returns_tool_not_found() -> None:
    registry = ToolRegistry()
    result = asyncio.run(registry.call("not_exists", {"x": 1}))
    assert result.status == ToolResultStatus.error
    assert result.error_code == "tool_not_found"


def test_tool_registry_timeout_retries_once_then_timeout() -> None:
    registry = ToolRegistry(default_timeout_seconds=0.005)
    tool = SlowTool()
    registry.register(tool)
    result = asyncio.run(registry.call("slow", {}))
    assert result.status == ToolResultStatus.timeout
    assert result.error_code == "tool_timeout"
    assert result.meta["attempts"] == 2
    assert tool.attempts == 2
