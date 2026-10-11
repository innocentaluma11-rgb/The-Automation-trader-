from __future__ import annotations

from collections import OrderedDict

from .agents.data_agent import DataAgent
from .agents.research_agent import ResearchAgent
from .agents.strategy_agent import StrategyAgent
from .agents.backtest_agent import BacktestAgent
from .agents.risk_agent import RiskAgent
from .agents.execution_agent import ExecutionAgent
from .agents.monitoring_agent import MonitoringAgent
from .agents.journal_agent import JournalAgent
from .agents.reporting_agent import ReportingAgent
from .agents.knowledge_agent import KnowledgeAgent
from .agents.orchestrator_agent import OrchestratorAgent
from .models import AgentContext, MarketSnapshot


class TFXAgentEcosystem:
    """Coordinates the AI agent workflow shown in the architecture diagram."""

    def __init__(self, market_snapshot: MarketSnapshot | None = None):
        if market_snapshot is None:
            market_snapshot = MarketSnapshot(
                symbol="XAU/USD",
                price=2341.12,
                volatility=0.014,
                sentiment=0.62,
                volume=128000,
                news_bias=0.38,
                strategy_bias=0.57,
                score=0.64,
                metadata={"session": "demo-run", "source": "simulated"},
            )

        self.market_snapshot = market_snapshot
        self.agents = OrderedDict(
            [
                ("01_data", DataAgent()),
                ("02_research_agent", ResearchAgent()),
                ("03_strategy_agent", StrategyAgent()),
                ("04_backtest_agent", BacktestAgent()),
                ("05_risk_agent", RiskAgent()),
                ("06_execution_agent", ExecutionAgent()),
                ("07_monitoring_agent", MonitoringAgent()),
                ("08_journal_agent", JournalAgent()),
                ("09_reporting_agent", ReportingAgent()),
                ("10_knowledge_agent", KnowledgeAgent()),
                ("11_orchestrator", OrchestratorAgent()),
            ]
        )

    def run_cycle(self, market_snapshot: MarketSnapshot | None = None):
        snapshot = market_snapshot or self.market_snapshot
        context = AgentContext(market=snapshot)
        results = []

        for _, agent in self.agents.items():
            result = agent.process(context)
            results.append(result)

        status = "complete" if all(r.status == "ok" for r in results) else "partial"
        summary = {
            "status": status,
            "symbol": snapshot.symbol,
            "market_price": snapshot.price,
            "portfolio_signal": context.strategy.get("signal"),
            "trade_action": context.execution.get("action"),
            "risk_state": context.risk.get("state"),
            "agents_processed": len(results),
        }
        context.reporting = {
            **context.reporting,
            "summary": summary,
            "agent_count": len(results),
        }
        return {"context": context, "results": results, "summary": summary}
