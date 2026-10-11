"""Strategy backtesting and walk-forward validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class Position(str, Enum):
    """Trade position state."""
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass
class Trade:
    """Represents a single executed trade."""
    entry_time: datetime
    entry_price: float
    position: Position
    size: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    bars_held: int = 0

    def close(self, exit_time: datetime, exit_price: float) -> None:
        """Close the trade and compute P&L."""
        self.exit_time = exit_time
        self.exit_price = exit_price
        if self.position == Position.LONG:
            self.pnl = (exit_price - self.entry_price) * self.size
            self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        elif self.position == Position.SHORT:
            self.pnl = (self.entry_price - exit_price) * self.size
            self.pnl_pct = ((self.entry_price - exit_price) / self.entry_price) * 100


@dataclass
class BacktestResult:
    """Summary metrics for a backtest run."""
    symbol: str
    start_time: datetime
    end_time: datetime
    initial_capital: float = 100000.0
    final_capital: float = 0.0
    total_return_pct: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    win_count: int = 0
    loss_count: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    equity_curve: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "initial_capital": self.initial_capital,
            "final_capital": round(self.final_capital, 2),
            "total_return_pct": round(self.total_return_pct, 2),
            "trade_count": len(self.trades),
            "win_count": self.win_count,
            "loss_count": self.loss_count,
            "win_rate": round(self.win_rate, 2),
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
            "max_drawdown": round(self.max_drawdown, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 2),
            "profit_factor": round(self.profit_factor, 2),
        }


class BacktestEngine:
    """Simulates strategy performance over historical data."""

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]

    def simulate_strategy(
        self,
        symbol: str,
        prices: List[float],
        signals: List[str],
        times: List[datetime],
    ) -> BacktestResult:
        """Run a backtest using a list of price bars and signals."""
        self.trades = []
        self.equity_curve = [self.initial_capital]
        current_position = None
        current_equity = self.initial_capital

        for i, (price, signal, time) in enumerate(zip(prices, signals, times)):
            if signal == "buy" and current_position is None:
                current_position = Trade(
                    entry_time=time,
                    entry_price=price,
                    position=Position.LONG,
                    size=1.0,
                )
            elif signal == "sell" and current_position is not None:
                current_position.close(time, price)
                current_position.bars_held = i - len([t for t in self.trades])
                self.trades.append(current_position)
                current_equity = self.initial_capital + sum(t.pnl for t in self.trades)
                self.equity_curve.append(current_equity)
                current_position = None

        if current_position is not None:
            current_position.close(times[-1], prices[-1])
            self.trades.append(current_position)
            current_equity = self.initial_capital + sum(t.pnl for t in self.trades)
            self.equity_curve.append(current_equity)

        return self._compute_metrics(
            symbol=symbol,
            start_time=times[0],
            end_time=times[-1],
            final_equity=current_equity,
        )

    def _compute_metrics(self, symbol: str, start_time: datetime, end_time: datetime, final_equity: float) -> BacktestResult:
        """Compute performance metrics from trades."""
        result = BacktestResult(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            initial_capital=self.initial_capital,
            final_capital=final_equity,
            total_return_pct=(final_equity - self.initial_capital) / self.initial_capital * 100,
            trades=self.trades,
            equity_curve=self.equity_curve,
        )

        if self.trades:
            wins = [t for t in self.trades if t.pnl > 0]
            losses = [t for t in self.trades if t.pnl < 0]
            result.win_count = len(wins)
            result.loss_count = len(losses)
            result.win_rate = len(wins) / len(self.trades) if self.trades else 0.0
            result.avg_win = np.mean([t.pnl for t in wins]) if wins else 0.0
            result.avg_loss = np.mean([t.pnl for t in losses]) if losses else 0.0

            if len(self.equity_curve) > 1:
                drawdowns = self._compute_drawdowns(self.equity_curve)
                result.max_drawdown = max(drawdowns) if drawdowns else 0.0

            gross_profit = sum(t.pnl for t in wins)
            gross_loss = abs(sum(t.pnl for t in losses))
            result.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        return result

    def _compute_drawdowns(self, equity_curve: List[float]) -> List[float]:
        """Compute drawdown at each point."""
        drawdowns = []
        running_max = equity_curve[0]
        for val in equity_curve:
            running_max = max(running_max, val)
            dd = (running_max - val) / running_max if running_max > 0 else 0.0
            drawdowns.append(dd)
        return drawdowns
