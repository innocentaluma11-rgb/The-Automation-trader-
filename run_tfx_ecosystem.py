"""TFX AI Agent Ecosystem - Main Entry Point

This script demonstrates running a complete cycle of the 11-agent ecosystem.
"""
from __future__ import annotations

from tfx_agents import MarketSnapshot, TFXAgentEcosystem


def main() -> None:
    """Run a single ecosystem cycle with a simulated market snapshot."""
    market_snapshot = MarketSnapshot(
        symbol="XAU/USD",
        price=2341.12,
        volatility=0.014,
        sentiment=0.68,
        volume=126000,
        news_bias=0.41,
        strategy_bias=0.58,
        score=0.71,
        metadata={"session": "demo-run", "source": "simulated"},
    )

    print("=" * 60)
    print("TFX AI Agent Ecosystem - Demo Run")
    print("=" * 60)
    print(f"\nMarket Snapshot: {market_snapshot.symbol} @ {market_snapshot.price}")
    print(f"Volatility: {market_snapshot.volatility:.4f} | Volume: {market_snapshot.volume:.0f}\n")

    ecosystem = TFXAgentEcosystem(market_snapshot=market_snapshot)
    result = ecosystem.run_cycle()

    print("Cycle Status: " + result["summary"]["status"].upper())
    print(f"Agents Processed: {result['summary']['agents_processed']}/11\n")

    print("Agent Results:")
    print("-" * 60)
    for agent_result in result["results"]:
        status_icon = "✓" if agent_result.status == "ok" else "✗"
        print(f"{status_icon} {agent_result.agent}: {agent_result.summary}")

    print("-" * 60)
    print("\nFinal Context State:")
    print(f"  Strategy Signal: {result['context'].strategy.get('signal', 'N/A')}")
    print(f"  Execution Action: {result['context'].execution.get('action', 'N/A')}")
    print(f"  Risk State: {result['context'].risk.get('state', 'N/A')}")
    print(f"  Monitoring Status: {result['context'].monitoring.get('status', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
