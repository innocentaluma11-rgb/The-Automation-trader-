from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AgentResult:
    agent: str
    status: str = "ok"
    summary: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketSnapshot:
    symbol: str = "XAU/USD"
    price: float = 0.0
    volatility: float = 0.0
    sentiment: float = 0.0
    volume: float = 0.0
    news_bias: float = 0.0
    strategy_bias: float = 0.0
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentContext:
    market: MarketSnapshot
    data: Dict[str, Any] = field(default_factory=dict)
    research: Dict[str, Any] = field(default_factory=dict)
    strategy: Dict[str, Any] = field(default_factory=dict)
    backtest: Dict[str, Any] = field(default_factory=dict)
    risk: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)
    journal: Dict[str, Any] = field(default_factory=dict)
    reporting: Dict[str, Any] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)
