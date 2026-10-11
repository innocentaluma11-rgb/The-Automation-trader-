from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class ReportingAgent(BaseAgent):
    """Creates concise daily, weekly, and performance summaries."""

    def __init__(self):
        super().__init__("09_reporting_agent", "Builds summaries for execution, risk, and performance reporting.")

    def process(self, context: AgentContext) -> AgentResult:
        signal = context.strategy.get("signal", "neutral")
        report = {
            "signal": signal,
            "report_type": "performance_summary",
            "status": "generated",
        }
        context.reporting = report
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Reporting workflow generated a {report['report_type']} for {signal}.",
            metrics=report,
        )
