from __future__ import annotations

import asyncio
from typing import Any

from src.contracts.tools import ToolResult, ToolResultStatus
from src.tools.base import BaseTool


class ToolRegistry:
    def __init__(
        self,
        *,
        default_timeout_seconds: float = 5.0,
        timeout_retry_once: bool = True,
    ) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._default_timeout_seconds = default_timeout_seconds
        self._timeout_retry_once = timeout_retry_once

    def register(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("Tool name must not be empty.")
        self._tools[tool.name] = tool

    async def call(
        self,
        name: str,
        payload: dict[str, Any],
        *,
        allowed_tools: set[str] | None = None,
        timeout_seconds: float | None = None,
        retry_on_timeout: bool | None = None,
    ) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(
                status=ToolResultStatus.error,
                error_code="tool_not_found",
                error_message=f"Tool '{name}' is not registered.",
                meta={"tool_name": name},
            )

        if allowed_tools is not None and name not in allowed_tools:
            return ToolResult(
                status=ToolResultStatus.denied,
                error_code="permission_denied",
                error_message=f"Tool '{name}' is not allowed in this context.",
                meta={"tool_name": name},
            )

        timeout = timeout_seconds or self._default_timeout_seconds
        should_retry = self._timeout_retry_once if retry_on_timeout is None else retry_on_timeout
        max_attempts = 2 if should_retry else 1

        for attempt in range(1, max_attempts + 1):
            try:
                data = await asyncio.wait_for(tool.execute(payload), timeout=timeout)
                return ToolResult(
                    status=ToolResultStatus.ok,
                    data=data,
                    meta={"tool_name": name, "attempts": attempt},
                )
            except asyncio.TimeoutError:
                if attempt < max_attempts:
                    continue
                return ToolResult(
                    status=ToolResultStatus.timeout,
                    error_code="tool_timeout",
                    error_message=f"Tool '{name}' timed out after {max_attempts} attempts.",
                    meta={
                        "tool_name": name,
                        "attempts": attempt,
                        "retry_count": max(0, attempt - 1),
                        "timeout_seconds": timeout,
                    },
                )
            except Exception as exc:  # pragma: no cover - defensive fallback
                return ToolResult(
                    status=ToolResultStatus.error,
                    error_code="tool_execution_error",
                    error_message=str(exc),
                    meta={"tool_name": name, "attempts": attempt},
                )

        return ToolResult(
            status=ToolResultStatus.error,
            error_code="tool_unreachable",
            error_message=f"Tool '{name}' reached an invalid execution branch.",
            meta={"tool_name": name},
        )
