from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class KnowledgeAgent(BaseAgent):
    """Maintains the reusable library of rules, docs, and prior outcomes."""

    def __init__(self):
        super().__init__("10_knowledge_agent", "Stores decision memory, strategy rules, and reusable context.")

    def process(self, context: AgentContext) -> AgentResult:
        memory = {
            "rules": ["risk-first sizing", "evidence-based execution"],
            "last_signal": context.strategy.get("signal", "neutral"),
        }
        context.knowledge = memory
        return AgentResult(
            agent=self.name,
            status="ok",
            summary="Knowledge base updated with the latest trade cycle.",
            metrics=memory,
        )
