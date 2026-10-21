from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    name: str = ""

    @abstractmethod
    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
