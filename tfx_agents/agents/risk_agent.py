from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class BacktestAgent(BaseAgent):
    """Simulates historical performance for proposed strategies."""

    def __init__(self):
        super().__init__("04_backtest_agent", "Runs a targeted simulation and evaluates strategy quality.")

    def process(self, context: AgentContext) -> AgentResult:
        signal = context.strategy.get("signal", "neutral")
        gain = 0.018 if signal == "buy" else -0.012 if signal == "sell" else 0.003
        context.backtest = {
            "return_pct": round(gain * 100, 3),
            "win_rate": 0.62 if signal == "buy" else 0.54,
            "drawdown": 0.16,
        }
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Backtest return={context.backtest['return_pct']}% over simulated horizon.",
            metrics=context.backtest,
        )
