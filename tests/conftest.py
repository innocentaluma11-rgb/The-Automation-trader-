from __future__ import annotations

import pytest


@pytest.fixture
def sample_market_snapshot():
    from tfx_agents import MarketSnapshot

    return MarketSnapshot(
        symbol="XAU/USD",
        price=2341.12,
        volatility=0.014,
        sentiment=0.68,
        volume=126000,
        news_bias=0.41,
        strategy_bias=0.58,
        score=0.71,
        metadata={"session": "pytest", "source": "simulated"},
    )


@pytest.fixture
def sample_agent_context(sample_market_snapshot):
    from tfx_agents import AgentContext

    return AgentContext(market=sample_market_snapshot)
