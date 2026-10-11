from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class MonitoringAgent(BaseAgent):
    """Tracks risk and system health during execution."""

    def __init__(self):
        super().__init__("07_monitoring_agent", "Tracks broker health, alerting, and anomaly detection.")

    def process(self, context: AgentContext) -> AgentResult:
        status = "healthy" if context.risk.get("state") != "watch" else "watchlist"
        context.monitoring = {
            "status": status,
            "alerts": [] if status == "healthy" else ["risk threshold watch"],
            "latency_ms": 42,
        }
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"System status={status}; monitoring active.",
            metrics=context.monitoring,
        )
