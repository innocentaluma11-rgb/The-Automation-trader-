from __future__ import annotations

from .base import BaseAgent
from .models import AgentContext, AgentResult


class OrchestratorAgent(BaseAgent):
    """Top-level controller that coordinates the ecosystem."""

    def __init__(self):
        super().__init__("11_orchestrator", "Coordinates execution, monitoring, reporting, and learning.")

    def process(self, context: AgentContext) -> AgentResult:
        signal = context.strategy.get("signal", "neutral")
        action = context.execution.get("action", "hold")
        risk_state = context.risk.get("state", "watch")
        summary = f"Signal={signal}, action={action}, risk={risk_state}."

        context.knowledge.setdefault("memory", []).append(summary)
        context.reporting.update(
            {
                "signal": signal,
                "action": action,
                "risk_state": risk_state,
                "status": "healthy",
            }
        )

        result = AgentResult(
            agent=self.name,
            status="ok",
            summary=summary,
            metrics={
                "signal": signal,
                "action": action,
                "risk_state": risk_state,
                "knowledge_entries": len(context.knowledge.get("memory", [])),
            },
        )
        return result
