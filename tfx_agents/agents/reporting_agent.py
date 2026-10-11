from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class JournalAgent(BaseAgent):
    """Records trade events and decision history."""

    def __init__(self):
        super().__init__("08_journal_agent", "Stores execution notes, screenshots, and trade annotations.")

    def process(self, context: AgentContext) -> AgentResult:
        entry = {
            "signal": context.strategy.get("signal"),
            "action": context.execution.get("action"),
            "phase": "closed_loop",
        }
        context.journal = {"entries": [entry], "last_action": entry["action"]}
        return AgentResult(
            agent=self.name,
            status="ok",
            summary="Journaled the latest trade cycle.",
            metrics=context.journal,
        )
