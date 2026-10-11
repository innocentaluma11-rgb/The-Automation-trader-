from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class StrategyAgent(BaseAgent):
    """Builds a trade signal from market data and research inputs."""

    def __init__(self):
        super().__init__("03_strategy_agent", "Generates a trade signal and strategy plan.")

    def process(self, context: AgentContext) -> AgentResult:
        market = context.market
        research = context.research
        signal_score = 0.4 * market.score + 0.3 * research.get("sentiment_score", 0.0) + 0.3 * market.strategy_bias
        signal = "buy" if signal_score > 0.6 else "sell" if signal_score < 0.4 else "neutral"
        context.strategy = {
            "signal": signal,
            "score": round(signal_score, 3),
            "structure": "momentum_follow_through",
        }
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Strategy signal={signal} with score {signal_score:.3f}.",
            metrics=context.strategy,
        )
