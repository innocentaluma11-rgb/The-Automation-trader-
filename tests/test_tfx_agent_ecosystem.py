from __future__ import annotations

from tfx_agents import MarketSnapshot, TFXAgentEcosystem


def main() -> None:
    market_snapshot = MarketSnapshot(
        symbol="XAU/USD",
        price=2341.12,
        volatility=0.014,
        sentiment=0.68,
        volume=126000,
        news_bias=0.41,
        strategy_bias=0.58,
        score=0.71,
        metadata={"session": "manual-demo", "source": "simulated"},
    )

    ecosystem = TFXAgentEcosystem(market_snapshot=market_snapshot)
    result = ecosystem.run_cycle()
    print("TFX AI Agent Ecosystem summary")
    print(result["summary"])
    for agent_result in result["results"]:
        print(f"- {agent_result.agent}: {agent_result.summary}")


if __name__ == "__main__":
    main()
