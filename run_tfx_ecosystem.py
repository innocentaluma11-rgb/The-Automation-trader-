from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class OrchestratorAgent(BaseAgent):
    """Top-level controller for signal-to-execution lifecycle."""

    def __init__(self):
        super().__init__("11_orchestrator", "Coordinates agent routing, scheduling, and end-to-end workflow control.")

    def process(self, context: AgentContext) -> AgentResult:
        signal = context.strategy.get("signal", "neutral")
        action = context.execution.get("action", "hold")
        risk_state = context.risk.get("state", "watch")
        summary = f"Cycle complete: {signal} signal -> {action} action -> {risk_state} risk posture."
        context.knowledge.setdefault("memory", []).append(summary)
        return AgentResult(
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
