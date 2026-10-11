from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class RiskAgent(BaseAgent):
    """Measures exposure, sizing, and risk control."""

    def __init__(self):
        super().__init__("05_risk_agent", "Controls drawdown, exposure, and position sizing." )

    def process(self, context: AgentContext) -> AgentResult:
        signal = context.strategy.get("signal", "neutral")
        exposure = 0.03 if signal == "buy" else 0.02 if signal == "sell" else 0.01
        state = "accept" if signal in {"buy", "sell"} else "watch"
        context.risk = {
            "exposure": round(exposure, 4),
            "max_drawdown": 0.12,
            "position_size": 0.5,
            "state": state,
        }
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Risk state={state} with exposure {exposure:.3f}.",
            metrics=context.risk,
        )
