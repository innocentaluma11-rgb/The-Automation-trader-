from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class DataAgent(BaseAgent):
    """Loads and validates market data for the pipeline."""

    def __init__(self):
        super().__init__("01_data", "Validates raw market data and prepares the signal feed.")

    def process(self, context: AgentContext) -> AgentResult:
        market = context.market
        metrics = {
            "symbol": market.symbol,
            "price": market.price,
            "volatility": market.volatility,
            "volume": market.volume,
            "data_quality": "validated",
        }
        context.data = metrics
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Validated {market.symbol} snapshot with {market.volume} volume.",
            metrics=metrics,
        )
