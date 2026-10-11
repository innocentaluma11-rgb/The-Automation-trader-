"""Market research and sentiment analysis module."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class SentimentLevel(str, Enum):
    """Sentiment classification."""
    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"


@dataclass
class NewsEvent:
    """A market news event with impact assessment."""
    timestamp: datetime
    headline: str
    source: str
    impact: float  # -1.0 to 1.0
    category: str  # e.g., "economic", "geopolitical", "corporate"
    sentiment_tags: List[str] = field(default_factory=list)


@dataclass
class MacroMetric:
    """Macroeconomic metric snapshot."""
    name: str
    value: float
    forecast: float
    previous: float
    unit: str
    timestamp: datetime
    surprise_index: float = 0.0  # deviation from forecast


class ResearchEngine:
    """Analyzes market fundamentals, macro, and sentiment."""

    def __init__(self):
        self.news_feed: List[NewsEvent] = []
        self.macro_metrics: List[MacroMetric] = []
        self.cache: Dict[str, Any] = {}

    def add_news_event(self, event: NewsEvent) -> None:
        """Ingest a news event."""
        self.news_feed.append(event)
        self._update_sentiment_cache()

    def add_macro_metric(self, metric: MacroMetric) -> None:
        """Ingest a macro metric."""
        self.macro_metrics.append(metric)
        self._update_macro_cache()

    def _update_sentiment_cache(self) -> None:
        """Recompute sentiment from recent news."""
        if not self.news_feed:
            self.cache["sentiment_score"] = 0.5
            return

        recent = self.news_feed[-20:]  # last 20 events
        impacts = [e.impact for e in recent]
        sentiment_score = 0.5 + np.mean(impacts) * 0.25
        self.cache["sentiment_score"] = np.clip(sentiment_score, 0.0, 1.0)
        self.cache["sentiment_level"] = self._score_to_level(self.cache["sentiment_score"])

    def _update_macro_cache(self) -> None:
        """Recompute macro bias from recent surprises."""
        if not self.macro_metrics:
            self.cache["macro_bias"] = 0.0
            return

        recent = self.macro_metrics[-10:]
        surprises = [m.surprise_index for m in recent]
        macro_bias = np.mean(surprises) if surprises else 0.0
        self.cache["macro_bias"] = np.clip(macro_bias, -1.0, 1.0)

    def _score_to_level(self, score: float) -> SentimentLevel:
        """Convert numeric score to sentiment level."""
        if score >= 0.8:
            return SentimentLevel.VERY_BULLISH
        elif score >= 0.6:
            return SentimentLevel.BULLISH
        elif score >= 0.4:
            return SentimentLevel.NEUTRAL
        elif score >= 0.2:
            return SentimentLevel.BEARISH
        else:
            return SentimentLevel.VERY_BEARISH

    def get_sentiment_report(self) -> Dict[str, Any]:
        """Generate a current sentiment and macro report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment_score": self.cache.get("sentiment_score", 0.5),
            "sentiment_level": self.cache.get("sentiment_level", SentimentLevel.NEUTRAL).value,
            "macro_bias": self.cache.get("macro_bias", 0.0),
            "recent_news_count": len(self.news_feed[-20:]),
            "recent_macro_events": len(self.macro_metrics[-10:]),
            "news_sources": list(set(e.source for e in self.news_feed[-20:])),
        }

    def scan_for_anomalies(self) -> Dict[str, Any]:
        """Flag unusual market conditions or data anomalies."""
        anomalies = []

        if self.macro_metrics:
            recent_surprises = [m.surprise_index for m in self.macro_metrics[-5:]]
            if any(abs(s) > 0.5 for s in recent_surprises):
                anomalies.append("high_macro_surprise")

        if self.news_feed:
            recent_impacts = [e.impact for e in self.news_feed[-5:]]
            if sum(1 for i in recent_impacts if abs(i) > 0.7) > 2:
                anomalies.append("volatile_news_environment")

        return {
            "has_anomalies": len(anomalies) > 0,
            "flags": anomalies,
        }
