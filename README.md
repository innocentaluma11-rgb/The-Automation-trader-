# TFX AI Agent Ecosystem

A multi-agent AI system for automated trading research, strategy validation, and risk management. The ecosystem coordinates 11 specialized agents through a complete trading decision cycle: from market data ingestion through execution and monitoring.

## Architecture

```
Market Data (01_DATA)
        ↓
Research Analysis (02_RESEARCH_AGENT)
        ↓
Strategy Generation (03_STRATEGY_AGENT)
        ↓
Backtesting (04_BACKTEST_AGENT)
        ↓
Risk Evaluation (05_RISK_AGENT)
        ↓
Execution (06_EXECUTION_AGENT)
        ↓
Monitoring (07_MONITORING_AGENT)
        ↓
Journal Logging (08_JOURNAL_AGENT)
        ↓
Reporting (09_REPORTING_AGENT)
        ↓
Knowledge Management (10_KNOWLEDGE_AGENT)
        ↓
Orchestration (11_ORCHESTRATOR)
```

## Quick Start

### Installation

```bash
git clone https://github.com/innocentaluma11-rgb/The-Automation-trader-.git
cd The-Automation-trader-
pip install -r requirements.txt
```

### Run Demo

```bash
python run_tfx_ecosystem.py
```

Expected output:
```
TFX AI Agent Ecosystem - Demo Run
Market Snapshot: XAU/USD @ 2341.12
...
✓ 01_data: Validated XAU/USD snapshot with 126000 volume.
✓ 02_research_agent: Research bias=bullish with sentiment 0.684.
... (9 more agents)
```

### Run Tests

```bash
pytest tests/ -v
```

## Project Structure

```
tfx_agents/
├── __init__.py              # Public API
├── base.py                  # BaseAgent contract
├── models.py                # Data models (AgentContext, MarketSnapshot, etc.)
├── orchestrator.py          # TFXAgentEcosystem main coordinator
├── agents/                  # Individual agent implementations
│   ├── data_agent.py        # 01_DATA
│   ├── research_agent.py    # 02_RESEARCH_AGENT
│   ├── strategy_agent.py    # 03_STRATEGY_AGENT
│   ├── backtest_agent.py    # 04_BACKTEST_AGENT
│   ├── risk_agent.py        # 05_RISK_AGENT
│   ├── execution_agent.py   # 06_EXECUTION_AGENT
│   ├── monitoring_agent.py  # 07_MONITORING_AGENT
│   ├── journal_agent.py     # 08_JOURNAL_AGENT
│   ├── reporting_agent.py   # 09_REPORTING_AGENT
│   ├── knowledge_agent.py   # 10_KNOWLEDGE_AGENT
│   └── orchestrator_agent.py # 11_ORCHESTRATOR
├── data_pipeline.py         # Market data ingestion & validation
├── market_research.py       # Sentiment & macro analysis
├── backtesting_engine.py    # Strategy simulation
├── risk_management.py       # Position sizing & risk controls
└── performance_monitor.py   # System health & P&L tracking

tests/
├── conftest.py              # pytest fixtures and configuration
├── test_core.py             # Core ecosystem and import tests
├── test_models.py           # Data model validation tests
└── test_data_pipeline.py    # Data pipeline tests

requirements.txt             # Python dependencies
.github/workflows/           # CI/CD workflows
```

## Key Components

### Models

- **MarketSnapshot**: Current market state (price, volatility, sentiment, volume)
- **AgentContext**: Shared state dictionary passed through the agent chain
- **AgentResult**: Output from each agent processing step

### Core Classes

- **BaseAgent**: Abstract base for all agents
- **TFXAgentEcosystem**: Main orchestrator that chains 11 agents
- **DataPipeline**: OHLCV data ingestion and validation
- **ResearchEngine**: Sentiment and macro analysis
- **BacktestEngine**: Strategy performance simulation
- **RiskManager**: Position sizing and drawdown controls
- **PerformanceMonitor**: System health and alerting

## Configuration

Create a `.env` file (copy `.env.example`):

```bash
cp .env.example .env
```

Example configuration:
```
PORTFOLIO_VALUE=100000
MAX_DRAWDOWN_LIMIT=0.15
DATA_SOURCE=csv
LIVE_TRADING=false
```

## Testing

The project uses pytest for testing:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest tests/ --cov=tfx_agents --cov-report=html
```

## CI/CD

GitHub Actions automatically runs tests on every push and pull request. See `.github/workflows/` for workflow definitions.

## Status

**Current Phase:** Foundation & Testing  
**Completed:**
- ✅ Core agent infrastructure
- ✅ Data models and context passing
- ✅ Entry point and basic demo
- ✅ Test framework setup
- ✅ CI/CD workflow

**In Progress:**
- 🔄 Agent integration tests
- 🔄 Data pipeline validation

**Planned:**
- [ ] Technical indicator calculations
- [ ] Advanced backtesting with transaction costs
- [ ] Real broker integration (paper trading first)
- [ ] Advanced monitoring and alerting

## Safety & Risk

⚠️ **Important:**
- This is a research and testing system, not production trading code
- No real broker connections are enabled
- All orders are simulated in demo mode
- Transaction costs and slippage not yet modeled
- Backtests assume ideal fills and perfect information

## License

MIT

## Support

For issues, questions, or contributions, open an issue on GitHub.
