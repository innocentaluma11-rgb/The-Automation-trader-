from __future__ import annotations

from .base import BaseAgent
from ..models import AgentContext, AgentResult


class ResearchAgent(BaseAgent):
    """Researches market context and news bias."""

    def __init__(self):
        super().__init__("02_research_agent", "Collects fundamental, sentiment, and macro research insights.")

    def process(self, context: AgentContext) -> AgentResult:
        market = context.market
        sentiment_score = market.sentiment + market.news_bias * 0.5
        context.research = {
            "sentiment_score": round(sentiment_score, 3),
            "macro_bias": "bullish" if sentiment_score > 0.5 else "neutral",
            "news_bias": market.news_bias,
        }
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Research bias={context.research['macro_bias']} with sentiment {sentiment_score:.3f}.",
            metrics=context.research,
        )
