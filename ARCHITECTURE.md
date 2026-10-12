## TFX AI Agent Ecosystem - Architecture Document

### Overview

The TFX (Trading Finance Ecosystem) is a **multi-agent orchestration system** designed to automate the complete trading decision cycle from market data ingestion through risk evaluation, strategy execution, monitoring, and learning.

The core design principle is **sequential agent chaining**: each of 11 specialized agents processes a shared context object, making decisions and enriching the state for downstream agents. This creates a transparent, auditable pipeline where each agent's output can be inspected and understood.

---

## Part 1: Core Architecture Layers

### Layer 1: Data Models (Foundation)

All agents communicate through three core dataclasses defined in `tfx_agents/models.py`:

#### 1. **MarketSnapshot** - Current Market State
```python
@dataclass
class MarketSnapshot:
    symbol: str              # Trading pair (e.g., "XAU/USD")
    price: float             # Current bid/ask midpoint
    volatility: float        # Historical/implied volatility
    sentiment: float         # Market sentiment score [0, 1]
    volume: float            # Current period trading volume
    news_bias: float         # News sentiment impact [-1, 1]
    strategy_bias: float     # Strategy-specific bias score
    score: float             # Composite market score [0, 1]
    metadata: Dict[str, Any] # Extensible fields (session, source, etc.)
```

**Purpose:** Read-only snapshot of market conditions. Passed into the ecosystem at the start of each cycle; never modified.

#### 2. **AgentContext** - Shared State Bus
```python
@dataclass
class AgentContext:
    market: MarketSnapshot           # Input market snapshot (read-only)
    
    # Agent-specific namespaces (written by each agent)
    data: Dict[str, Any]             # 01_DATA writes validation results
    research: Dict[str, Any]         # 02_RESEARCH writes sentiment analysis
    strategy: Dict[str, Any]         # 03_STRATEGY writes signal & confidence
    backtest: Dict[str, Any]         # 04_BACKTEST writes performance metrics
    risk: Dict[str, Any]             # 05_RISK writes position sizing & state
    execution: Dict[str, Any]        # 06_EXECUTION writes order details
    monitoring: Dict[str, Any]       # 07_MONITORING writes health alerts
    journal: Dict[str, Any]          # 08_JOURNAL writes trade history
    reporting: Dict[str, Any]        # 09_REPORTING writes summaries
    knowledge: Dict[str, Any]        # 10_KNOWLEDGE writes memory & rules
```

**Design Pattern:** Each agent reads from *upstream* namespaces (strategy reads data and research) and writes only to its own namespace. This prevents circular dependencies and makes data flow explicit.

#### 3. **AgentResult** - Agent Output Contract
```python
@dataclass
class AgentResult:
    agent: str               # Agent identifier (e.g., "01_data")
    status: str              # "ok" | "warning" | "error"
    summary: str             # Human-readable summary
    metrics: Dict[str, Any]  # Structured output metrics
```

**Purpose:** Each agent returns a result. The orchestrator collects these and reports pass/fail status.

---

### Layer 2: Agent Base Class

**File:** `tfx_agents/base.py`

```python
class BaseAgent:
    """Contract all agents must implement."""
    
    def __init__(self, name: str, description: str):
        self.name = name                    # e.g., "01_data"
        self.description = description      # e.g., "Validates market data"
    
    def process(self, context: AgentContext) -> AgentResult:
        """Core method: read context, compute, write result."""
        raise NotImplementedError()
```

**Design Pattern:**
- All agents inherit from `BaseAgent`
- Each agent is stateless (all state flows through `AgentContext`)
- `process()` is the single entry point
- Agents cannot directly call each other; communication is only through context

---

### Layer 3: Orchestrator (Sequential Executor)

**File:** `tfx_agents/orchestrator.py`

```python
class TFXAgentEcosystem:
    """Chains 11 agents in sequence."""
    
    def __init__(self, market_snapshot: MarketSnapshot | None = None):
        self.agents = OrderedDict([
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
        ])
    
    def run_cycle(self, market_snapshot: MarketSnapshot | None = None):
        """Execute all agents in order."""
        context = AgentContext(market=snapshot)
        results = []
        
        for agent_key, agent in self.agents.items():
            result = agent.process(context)  # Agent reads & writes context
            results.append(result)
        
        return {
            "context": context,          # Final state after all agents
            "results": results,          # Individual agent outputs
            "summary": {...}             # High-level cycle summary
        }
```

**Execution Flow:**

```
START
  |
  v
01_DATA: Validate market data
  |-- Reads: market.price, market.volume
  |-- Writes: context.data["sma", "volatility", "validation_errors"]
  |
  v
02_RESEARCH: Analyze sentiment & macro
  |-- Reads: market.sentiment, market.news_bias, context.data
  |-- Writes: context.research["sentiment_score", "macro_bias"]
  |
  v
03_STRATEGY: Generate trading signal
  |-- Reads: market.score, context.data, context.research
  |-- Writes: context.strategy["signal", "confidence", "score"]
  |
  v
04_BACKTEST: Simulate strategy performance
  |-- Reads: context.strategy["signal"]
  |-- Writes: context.backtest["return_pct", "win_rate", "drawdown"]
  |
  v
05_RISK: Evaluate position sizing & limits
  |-- Reads: market.volatility, context.strategy, context.backtest
  |-- Writes: context.risk["exposure", "position_size", "state"]
  |
  v
06_EXECUTION: Route to broker/simulator
  |-- Reads: context.strategy["signal"], context.risk["state"]
  |-- Writes: context.execution["action", "limit_price", "volume"]
  |
  v
07_MONITORING: Health checks & alerts
  |-- Reads: context.risk["state"], context.execution["action"]
  |-- Writes: context.monitoring["status", "alerts", "latency_ms"]
  |
  v
08_JOURNAL: Log trade event
  |-- Reads: context.strategy["signal"], context.execution["action"]
  |-- Writes: context.journal["entries", "last_action"]
  |
  v
09_REPORTING: Generate summary
  |-- Reads: All namespaces
  |-- Writes: context.reporting["summary", "status"]
  |
  v
10_KNOWLEDGE: Update decision memory
  |-- Reads: context.strategy, context.execution
  |-- Writes: context.knowledge["memory", "rules"]
  |
  v
11_ORCHESTRATOR: Finalize & aggregate
  |-- Reads: All namespaces
  |-- Writes: Final summary & validation
  |
  v
RETURN {context, results, summary}
```

---

## Part 2: The 11 Agents

### Agent 1: DataAgent (01_DATA)

**Purpose:** Ingest and validate market data

**Reads:**
- `context.market` — the MarketSnapshot

**Writes:**
- `context.data["price"]`
- `context.data["volume"]`
- `context.data["volatility"]`
- `context.data["validation_errors"]`

**Pseudocode:**
```python
def process(self, context):
    market = context.market
    # In production, would call DataPipeline to load OHLCV data
    # For now: validate snapshot fields
    context.data = {
        "symbol": market.symbol,
        "price": market.price,
        "volume": market.volume,
        "volatility": market.volatility,
        "data_quality": "validated" if market.price > 0 else "error"
    }
    return AgentResult(
        agent="01_data",
        status="ok",
        summary=f"Validated {market.symbol} snapshot..."
    )
```

**Intended Integration:** Will call `DataPipeline.load_csv()` or `DataPipeline.generate_synthetic_data()` to load OHLCV candles and compute technical indicators.

---

### Agent 2: ResearchAgent (02_RESEARCH_AGENT)

**Purpose:** Analyze market fundamentals and sentiment

**Reads:**
- `context.market.sentiment`
- `context.market.news_bias`
- `context.data` (optional, for corroboration)

**Writes:**
- `context.research["sentiment_score"]`
- `context.research["macro_bias"]`
- `context.research["sentiment_level"]` (enum: VERY_BEARISH, BEARISH, NEUTRAL, BULLISH, VERY_BULLISH)

**Pseudocode:**
```python
def process(self, context):
    market = context.market
    # Combine multiple sentiment sources
    sentiment_score = market.sentiment + market.news_bias * 0.5
    macro_bias = "bullish" if sentiment_score > 0.5 else "neutral"
    
    context.research = {
        "sentiment_score": sentiment_score,
        "macro_bias": macro_bias,
        "news_bias": market.news_bias,
    }
    return AgentResult(...)
```

**Intended Integration:** Will call `ResearchEngine` to:
- Ingest news events and compute sentiment from NLP
- Fetch macro metric surprises (CPI, unemployment, etc.)
- Generate anomaly flags (e.g., "high_macro_surprise")

---

### Agent 3: StrategyAgent (03_STRATEGY_AGENT)

**Purpose:** Generate a trading signal based on technical + sentiment inputs

**Reads:**
- `context.market.score` (composite market strength)
- `context.research["sentiment_score"]`
- `context.market.strategy_bias` (user-provided bias input)
- `context.data` (technical indicators, when available)

**Writes:**
- `context.strategy["signal"]` → "buy" | "sell" | "neutral"
- `context.strategy["confidence"]` → [0, 1]
- `context.strategy["score"]` → composite signal score

**Pseudocode:**
```python
def process(self, context):
    market = context.market
    research = context.research
    
    # Weighted combination of inputs
    signal_score = (
        0.4 * market.score + 
        0.3 * research.get("sentiment_score", 0.0) + 
        0.3 * market.strategy_bias
    )
    
    signal = "buy" if signal_score > 0.6 else "sell" if signal_score < 0.4 else "neutral"
    
    context.strategy = {
        "signal": signal,
        "confidence": abs(signal_score - 0.5) * 2,  # Distance from neutral
        "score": signal_score,
    }
    return AgentResult(...)
```

**Intended Integration:** Will call real technical indicator library (TA-Lib, pandas-ta) to compute:
- Moving averages (SMA, EMA)
- Oscillators (RSI, MACD, Stochastic)
- Bollinger Bands
- Pattern recognition

---

### Agent 4: BacktestAgent (04_BACKTEST_AGENT)

**Purpose:** Validate the strategy's historical performance

**Reads:**
- `context.strategy["signal"]`
- `context.data` (OHLCV candles, when available)

**Writes:**
- `context.backtest["return_pct"]`
- `context.backtest["win_rate"]`
- `context.backtest["drawdown"]`
- `context.backtest["sharpe_ratio"]` (when computed)

**Pseudocode:**
```python
def process(self, context):
    signal = context.strategy.get("signal", "neutral")
    
    # Currently hardcoded; will call BacktestEngine
    gain = 0.018 if signal == "buy" else -0.012 if signal == "sell" else 0.003
    
    context.backtest = {
        "return_pct": gain * 100,
        "win_rate": 0.62 if signal == "buy" else 0.54,
        "drawdown": 0.16,
    }
    return AgentResult(...)
```

**Intended Integration:** Will call `BacktestEngine.simulate_strategy()` with:
- Historical OHLCV data (50-200 candles)
- Generated signals for each bar
- Compute metrics: max drawdown, Sharpe ratio, profit factor, etc.

**Critical Note:** Backtesting does NOT yet include:
- Transaction costs (spread, slippage, commission)
- Partial fills or rejections
- Look-ahead bias detection
- Walk-forward validation

These are planned for Phase 3 of development.

---

### Agent 5: RiskAgent (05_RISK_AGENT)

**Purpose:** Size positions and enforce portfolio risk limits

**Reads:**
- `context.strategy["signal"]`
- `context.backtest["win_rate"]`
- `context.market.volatility`

**Writes:**
- `context.risk["exposure"]` → [0, 1] % of portfolio
- `context.risk["position_size"]` → contracts/lots
- `context.risk["state"]` → "accept" | "watch" | "reduce" | "lock"
- `context.risk["stop_loss"]` → price level
- `context.risk["take_profit"]` → price level

**Pseudocode:**
```python
def process(self, context):
    signal = context.strategy.get("signal", "neutral")
    
    # Risk state evaluation
    exposure = 0.03 if signal == "buy" else 0.02 if signal == "sell" else 0.01
    state = "accept" if signal in {"buy", "sell"} else "watch"
    
    context.risk = {
        "exposure": exposure,
        "max_drawdown": 0.12,
        "position_size": 0.5,
        "state": state,
    }
    return AgentResult(...)
```

**Intended Integration:** Will call `RiskManager` to:
- Compute position size based on Kelly Criterion or fixed-fraction
- Evaluate current portfolio drawdown
- Trigger risk state changes (WATCH → REDUCE → LOCK)
- Calculate stop-loss and take-profit levels
- **Enforce a risk "veto"** that can block execution if limits breached

**Critical Requirement:** Risk controls MUST be checked by ExecutionAgent before any order is routed.

---

### Agent 6: ExecutionAgent (06_EXECUTION_AGENT)

**Purpose:** Route approved trades to the broker or simulator

**Reads:**
- `context.strategy["signal"]`
- `context.risk["state"]` ← **MUST CHECK THIS**
- `context.market.price`

**Writes:**
- `context.execution["action"]` → "buy" | "sell" | "hold"
- `context.execution["limit_price"]`
- `context.execution["volume"]`
- `context.execution["route"]` → "broker_primary" | "simulator"

**Pseudocode:**
```python
def process(self, context):
    signal = context.strategy.get("signal", "neutral")
    risk_state = context.risk.get("state", "watch")
    
    # Risk veto: if LOCK, do NOT trade
    if risk_state == "lock":
        action = "hold"
    else:
        action = "buy" if signal == "buy" else "sell" if signal == "sell" else "hold"
    
    context.execution = {
        "action": action,
        "limit_price": context.market.price,
        "volume": 0.75,
        "route": "broker_primary" if action != "hold" else "none",
    }
    return AgentResult(...)
```

**Intended Integration:** Will:
- Check risk state; reject trade if LOCK
- Route to broker adapter (IB, CCXT, etc.) or paper trading simulator
- Record order ID and timestamp
- Handle partial fills and rejections

**Live Trading Safety:** This agent is the final checkpoint. It **will not send live orders** until explicit config flag is set (LIVE_TRADING=true).

---

### Agent 7: MonitoringAgent (07_MONITORING_AGENT)

**Purpose:** Track system health, latency, and P&L

**Reads:**
- `context.risk["state"]`
- `context.execution["action"]`
- Latency from prior agent calls

**Writes:**
- `context.monitoring["status"]` → "healthy" | "watchlist" | "critical"
- `context.monitoring["alerts"]` → list of alert messages
- `context.monitoring["latency_ms"]` → average processing time

**Pseudocode:**
```python
def process(self, context):
    risk_state = context.risk.get("state", "watch")
    
    status = "healthy" if risk_state != "watch" else "watchlist"
    alerts = [] if status == "healthy" else ["risk threshold watch"]
    
    context.monitoring = {
        "status": status,
        "alerts": alerts,
        "latency_ms": 42,
    }
    return AgentResult(...)
```

**Intended Integration:** Will call `PerformanceMonitor` to:
- Track execution latency for each agent
- Record P&L for closed trades
- Generate alerts for anomalies (e.g., data staleness, drawdown, connection loss)
- Maintain history for reporting

---

### Agent 8: JournalAgent (08_JOURNAL_AGENT)

**Purpose:** Log every trade decision for audit and learning

**Reads:**
- `context.strategy["signal"]`
- `context.execution["action"]`
- Market state at execution time

**Writes:**
- `context.journal["entries"]` → list of trade records
- `context.journal["last_action"]` → most recent action taken

**Pseudocode:**
```python
def process(self, context):
    entry = {
        "signal": context.strategy.get("signal"),
        "action": context.execution.get("action"),
        "phase": "closed_loop",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    context.journal = {
        "entries": [entry],
        "last_action": entry["action"],
    }
    return AgentResult(...)
```

**Intended Integration:** Will:
- Write to persistent storage (JSON, database, or CSV)
- Record entry/exit prices and P&L
- Attach annotations (user notes, error flags)
- Support later replay for backtesting

---

### Agent 9: ReportingAgent (09_REPORTING_AGENT)

**Purpose:** Summarize cycle results for human and machine consumption

**Reads:**
- All context namespaces (data, strategy, backtest, risk, execution, etc.)

**Writes:**
- `context.reporting["summary"]` → high-level report
- `context.reporting["status"]` → "generated"
- `context.reporting["report_type"]` → "performance_summary" | "daily" | "weekly"

**Pseudocode:**
```python
def process(self, context):
    signal = context.strategy.get("signal", "neutral")
    
    report = {
        "signal": signal,
        "report_type": "performance_summary",
        "status": "generated",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    context.reporting = report
    return AgentResult(...)
```

**Intended Integration:** Will generate:
- HTML reports with charts (matplotlib/plotly)
- JSON API endpoints for dashboard
- Email alerts for key events
- CSV exports for manual analysis

---

### Agent 10: KnowledgeAgent (10_KNOWLEDGE_AGENT)

**Purpose:** Maintain reusable decision memory and strategy rules

**Reads:**
- `context.strategy["signal"]`
- `context.execution["action"]`
- Historical trade results

**Writes:**
- `context.knowledge["memory"]` → decision history
- `context.knowledge["rules"]` → active trading rules
- `context.knowledge["prior_outcomes"]` → past similar situations

**Pseudocode:**
```python
def process(self, context):
    memory = {
        "rules": [
            "risk-first sizing",
            "evidence-based execution",
        ],
        "last_signal": context.strategy.get("signal", "neutral"),
    }
    
    context.knowledge = memory
    return AgentResult(...)
```

**Intended Integration:** Will:
- Store decision history in vector database (for similarity search)
- Retrieve prior outcomes for similar market conditions
- Update strategy rules based on recent performance
- Support "explain this decision" queries
- Enable reinforcement learning to update weights

---

### Agent 11: OrchestratorAgent (11_ORCHESTRATOR)

**Purpose:** Finalize and validate the complete cycle

**Reads:**
- All context namespaces (final state after 10 agents)

**Writes:**
- `context.reporting["summary"]` → final cycle summary
- Validates all agents succeeded

**Pseudocode:**
```python
def process(self, context):
    signal = context.strategy.get("signal", "neutral")
    action = context.execution.get("action", "hold")
    risk_state = context.risk.get("state", "watch")
    
    summary = f"Cycle complete: {signal} signal -> {action} action -> {risk_state} risk."
    
    context.knowledge.setdefault("memory", []).append(summary)
    
    return AgentResult(
        agent="11_orchestrator",
        status="ok",
        summary=summary,
        metrics={
            "signal": signal,
            "action": action,
            "risk_state": risk_state,
            "knowledge_entries": len(context.knowledge.get("memory", [])),
        },
    )
```

---

## Part 3: Supporting Engine Modules

### DataPipeline (`tfx_agents/data_pipeline.py`)

Manages OHLCV market data ingestion, validation, and technical indicator computation.

**Key Classes:**
- `OHLCV` — candlestick data (time, open, high, low, close, volume)
- `MarketDataCache` — in-memory candle cache with time-range queries
- `DataPipeline` — orchestrates loading, validation, and indicator calculation

**Key Methods:**
```python
pipeline = DataPipeline(symbol="XAU/USD")

# Load from CSV
pipeline.load_csv(Path("xauusd_test_data.csv"))

# Or generate synthetic data for testing
pipeline.generate_synthetic_data(bars=100, start_price=2341.0)

# Validate data integrity
validation = pipeline.validate_candles()  # Returns {valid, errors, stats}

# Compute technical indicators
indicators = pipeline.compute_indicators(window=20)  
# Returns {sma_20, volatility, volume_sma, latest_close}
```

**Status:** Fully implemented but not yet integrated into DataAgent.

---

### ResearchEngine (`tfx_agents/market_research.py`)

Analyzes market fundamentals and generates sentiment scores.

**Key Classes:**
- `NewsEvent` — represents a market news event with impact score
- `MacroMetric` — macroeconomic metric with surprise index
- `ResearchEngine` — ingests events and computes sentiment

**Key Methods:**
```python
engine = ResearchEngine()

# Add a news event
event = NewsEvent(
    timestamp=datetime.utcnow(),
    headline="Fed cuts rates",
    source="Reuters",
    impact=0.15,  # bullish
    category="monetary_policy",
)
engine.add_news_event(event)

# Get current sentiment
report = engine.get_sentiment_report()
# Returns {sentiment_score, sentiment_level, macro_bias, news_sources, ...}

# Detect market anomalies
anomalies = engine.scan_for_anomalies()
# Returns {has_anomalies, flags: ["high_macro_surprise", ...]}
```

**Status:** Fully implemented but not yet connected to live news/macro data sources.

---

### BacktestEngine (`tfx_agents/backtesting_engine.py`)

Simulates strategy performance over historical data.

**Key Classes:**
- `Trade` — represents a single entry/exit trade
- `BacktestResult` — summary metrics from a backtest run
- `BacktestEngine` — orchestrates the simulation

**Key Methods:**
```python
engine = BacktestEngine(initial_capital=100000.0)

# Simulate a strategy
prices = [100.0, 101.0, 102.5, 101.8, 103.0]
signals = ["buy", "sell", "hold", "buy", "sell"]
times = [datetime.utcnow() + timedelta(hours=i) for i in range(5)]

result = engine.simulate_strategy(
    symbol="XAU/USD",
    prices=prices,
    signals=signals,
    times=times,
)

# Inspect results
print(f"Return: {result.total_return_pct}%")
print(f"Win Rate: {result.win_rate}")
print(f"Max Drawdown: {result.max_drawdown}")
```

**Status:** Fully implemented but **backtesting has known biases**:
- No transaction costs (spread, slippage, commission)
- Assumes perfect fills at market price
- No partial fills or order rejections
- No look-ahead bias detection

These will be addressed in Phase 3.

---

### RiskManager (`tfx_agents/risk_management.py`)

Computes position sizing and enforces portfolio risk limits.

**Key Classes:**
- `RiskState` — enum: ACCEPT, WATCH, REDUCE, LOCK
- `RiskSnapshot` — current portfolio risk metrics
- `RiskManager` — enforces limits and computes position sizes

**Key Methods:**
```python
manager = RiskManager(portfolio_value=100000.0)

# Compute position size based on volatility and signal strength
size = manager.compute_position_size(
    signal_strength=0.72,
    volatility=0.015,
    max_risk_per_trade=0.02,  # 2% of portfolio per trade
)

# Evaluate current risk state
state = manager.evaluate_risk_state()  # Returns RiskState enum

# Compute stop-loss and take-profit
stops = manager.apply_stops_and_limits(
    entry_price=2341.12,
    current_price=2343.50,
    position_size=1.0,
    stop_loss_pct=0.02,   # 2% stop loss
    take_profit_pct=0.05,  # 5% take profit
)
# Returns {stop_loss, take_profit, current_pnl_pct, should_close, close_reason}
```

**Status:** Fully implemented but not yet integrated into risk agent or enforced by execution agent.

---

### PerformanceMonitor (`tfx_agents/performance_monitor.py`)

Tracks system health, P&L, latency, and generates alerts.

**Key Classes:**
- `AlertSeverity` — enum: INFO, WARNING, CRITICAL
- `Alert` — system or trading alert
- `PerformanceMetrics` — aggregated performance snapshot
- `PerformanceMonitor` — tracks health and generates alerts

**Key Methods:**
```python
monitor = PerformanceMonitor()

# Record execution latency
monitor.record_latency(latency_ms=42.5)

# Record a closed trade
monitor.record_trade(pnl=125.50, side="buy")

# Generate an alert
monitor.add_alert(
    severity=AlertSeverity.WARNING,
    component="data_pipeline",
    message="Price deviation detected: 5.2% from expected",
    context={"current": 2343, "expected": 2230},
)

# Generate performance report
report = monitor.generate_report()
# Returns PerformanceMetrics with all aggregated stats
```

**Status:** Fully implemented but not yet integrated into monitoring agent.

---

## Part 4: Data Flow Example (End-to-End)

**Scenario:** User creates a market snapshot and runs one ecosystem cycle.

```python
# Step 0: Create input
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

# Step 1: Initialize ecosystem
ecosystem = TFXAgentEcosystem(market_snapshot=market)

# Step 2: Run cycle (calls all 11 agents in sequence)
output = ecosystem.run_cycle()

# Step 3: Inspect output
print(output["summary"])
# {
#   "status": "complete",
#   "symbol": "XAU/USD",
#   "market_price": 2341.12,
#   "portfolio_signal": "buy",
#   "trade_action": "buy",
#   "risk_state": "accept",
#   "agents_processed": 11,
# }

# Step 4: Inspect individual agent results
for result in output["results"]:
    print(f"{result.agent}: {result.summary}")
# 01_data: Validated XAU/USD snapshot with 126000 volume.
# 02_research_agent: Research bias=bullish with sentiment 0.684.
# 03_strategy_agent: Strategy signal=buy with score 0.682.
# ... etc

# Step 5: Inspect final context state
context = output["context"]
print(context.strategy)     # {"signal": "buy", "confidence": 0.72, "score": 0.682}
print(context.risk)         # {"exposure": 0.03, "position_size": 0.5, "state": "accept"}
print(context.execution)    # {"action": "buy", "limit_price": 2341.12, "volume": 0.75}
```

---

## Part 5: Design Principles & Constraints

### 1. **Transparency**
Every agent's computation is visible in its output. No hidden state. All decisions can be audited.

### 2. **Composability**
Agents can be replaced or reordered without breaking the system. Each agent is independent.

### 3. **Fail-Safe**
If any agent sets `status="error"`, the orchestrator detects it. The system can be configured to halt trading on errors.

### 4. **No Circular Dependencies**
Agents only read from upstream agents. No back-channel communication.

### 5. **Extensibility**
New agents can be added by:
- Inheriting from `BaseAgent`
- Implementing `process(context) -> AgentResult`
- Adding to the orchestrator's `self.agents` OrderedDict

### 6. **Simulation-First**
All agents operate on synthetic/simulated data by default. Live broker connections must be explicitly enabled.

### 7. **Risk-First**
Risk controls (Agent 05) can veto execution (Agent 06). No trade goes through if risk limits breached.

---

## Part 6: Known Limitations & Future Work

### Current Limitations

1. **Agent Stubs**
   - Agents 1-10 are currently skeletal implementations with hardcoded logic
   - Real technical indicators, sentiment analysis, and backtesting not yet integrated

2. **Backtesting Biases**
   - No transaction costs
   - No slippage modeling
   - No partial fills or rejections
   - No look-ahead bias detection

3. **Data Pipeline**
   - No live data feeds (Alpaca, CCXT, etc.)
   - No real sentiment/macro data sources
   - Only synthetic and CSV file support

4. **Execution**
   - No real broker integrations
   - No paper trading mode
   - No order management (modify, cancel)

5. **Monitoring**
   - No persistent alert storage
   - No dashboard/UI
   - No email/SMS notifications

### Phase 1: Foundation (Weeks 1-2) ✅
- ✅ Core data models and agent infrastructure
- ✅ Orchestrator and 11-agent skeleton
- ✅ Entry point and demo runner
- ✅ Pytest foundation

### Phase 2: Integration (Weeks 3-4) 🔄
- 🔄 Wire DataPipeline into DataAgent
- 🔄 Wire ResearchEngine into ResearchAgent
- 🔄 Wire BacktestEngine into BacktestAgent
- 🔄 Wire RiskManager into RiskAgent
- [ ] Risk veto enforcement in ExecutionAgent

### Phase 3: Realism (Weeks 5-6)
- [ ] Transaction costs and slippage in backtesting
- [ ] Walk-forward validation
- [ ] Technical indicator calculations (TA-Lib)
- [ ] Real sentiment/macro data sources

### Phase 4: Production (Weeks 7+)
- [ ] Real broker integrations (IB, CCXT)
- [ ] Paper trading mode
- [ ] Advanced monitoring and alerting
- [ ] Reinforcement learning in KnowledgeAgent

---

## Part 7: How to Extend the Architecture

### Example: Add a New Agent

```python
# 1. Create tfx_agents/agents/custom_agent.py
from tfx_agents.base import BaseAgent
from tfx_agents.models import AgentContext, AgentResult

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="12_custom",
            description="My custom trading logic"
        )
    
    def process(self, context: AgentContext) -> AgentResult:
        # Read from upstream agents
        signal = context.strategy.get("signal")
        risk_state = context.risk.get("state")
        
        # Compute something new
        my_result = "computed_value"
        
        # Write to your own namespace
        context.custom = {
            "my_result": my_result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return AgentResult(
            agent=self.name,
            status="ok",
            summary=f"Custom agent processed signal={signal}",
            metrics={"my_result": my_result},
        )

# 2. Register in orchestrator.py
self.agents = OrderedDict([
    # ... (all 11 agents)
    ("12_custom", CustomAgent()),
])
```

---

## Summary

The TFX Ecosystem is a **modular, sequential, agent-based system** for automating trading decisions. Each of 11 agents specializes in one aspect of the decision cycle, reading from the shared `AgentContext` state bus and writing results. The orchestrator chains them in sequence, ensuring data flows from raw market data → research → strategy → backtesting → risk → execution → monitoring → learning.

The architecture is intentionally transparent (no hidden state), extensible (easy to add agents), and safe (risk controls can veto trades). It's ready for integration of real data pipelines, broker APIs, and advanced analytics.

