from __future__ import annotations

from typing import Any


class BaseAgent:
    """Common contract for all agents in the TFX ecosystem."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def process(self, context: Any) -> Any:
        raise NotImplementedError("Each agent must implement process().")
