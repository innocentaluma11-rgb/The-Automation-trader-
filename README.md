from __future__ import annotations

from tfx_agents import MarketSnapshot, TFXAgentEcosystem


def test_ecosystem_runs_and_reports_complete_cycle():
    market = MarketSnapshot(
        symbol="XAU/USD",
        price=2341.12,
        volatility=0.014,
        sentiment=0.68,
        volume=126000,
        news_bias=0.41,
        strategy_bias=0.58,
        score=0.71,
    )

    ecosystem = TFXAgentEcosystem(market_snapshot=market)
    output = ecosystem.run_cycle()

    assert output["summary"]["status"] == "complete"
    assert output["summary"]["symbol"] == "XAU/USD"
    assert len(output["results"]) == 11
    assert output["context"].execution["action"] in {"buy", "sell", "hold"}
    assert output["context"].strategy["signal"] in {"buy", "sell", "neutral"}
