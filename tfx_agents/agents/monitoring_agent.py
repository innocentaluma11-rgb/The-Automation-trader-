from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class ExecutionAgent(BaseAgent):
    """Converts risk-approved strategy into an order action."""

    def __init__(self):
        super().__init__("06_execution_agent", "Routes valid orders through the broker and execution engine.")

    def process(self, context: AgentContext) -> AgentResult:
        signal = context.strategy.get("signal", "neutral")
        action = "buy" if signal == "buy" else "sell" if signal == "sell" else "hold"
        context.execution = {
            "action": action,
            "limit_price": context.market.price,
            "volume": 0.75,
            "route": "broker_primary",
        }
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Execution action={action} routed through {context.execution['route']}.",
            metrics=context.execution,
        )
