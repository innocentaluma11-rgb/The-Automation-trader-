"""Position sizing and risk control logic."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import numpy as np


class RiskState(str, Enum):
    """Portfolio risk posture."""
    ACCEPT = "accept"
    WATCH = "watch"
    REDUCE = "reduce"
    LOCK = "lock"


@dataclass
class RiskSnapshot:
    """Current risk metrics and constraints."""
    portfolio_value: float = 100000.0
    current_drawdown: float = 0.0
    max_drawdown_limit: float = 0.15
    max_position_size: float = 0.05
    leverage: float = 1.0
    active_positions: int = 0
    daily_loss_limit: float = 0.02
    current_daily_loss: float = 0.0
    volatility_scalar: float = 1.0
    state: RiskState = RiskState.WATCH

    def to_dict(self) -> Dict[str, Any]:
        return {
            "portfolio_value": round(self.portfolio_value, 2),
            "current_drawdown": round(self.current_drawdown, 4),
            "max_drawdown_limit": round(self.max_drawdown_limit, 4),
            "max_position_size": round(self.max_position_size, 4),
            "leverage": round(self.leverage, 2),
            "active_positions": self.active_positions,
            "daily_loss_limit": round(self.daily_loss_limit, 4),
            "current_daily_loss": round(self.current_daily_loss, 4),
            "volatility_scalar": round(self.volatility_scalar, 3),
            "state": self.state.value,
        }


class RiskManager:
    """Enforces position sizing, drawdown, and exposure limits."""

    def __init__(self, portfolio_value: float = 100000.0):
        self.snapshot = RiskSnapshot(portfolio_value=portfolio_value)

    def compute_position_size(
        self,
        signal_strength: float,
        volatility: float,
        max_risk_per_trade: float = 0.02,
    ) -> float:
        """Calculate position size based on signal and volatility."""
        if volatility == 0.0:
            return 0.0

        base_size = (self.snapshot.portfolio_value * max_risk_per_trade) / volatility
        scaled_size = base_size * signal_strength * self.snapshot.volatility_scalar
        max_size = self.snapshot.portfolio_value * self.snapshot.max_position_size
        return min(scaled_size, max_size)

    def evaluate_risk_state(self) -> RiskState:
        """Determine portfolio risk posture."""
        if self.snapshot.current_daily_loss >= self.snapshot.daily_loss_limit:
            self.snapshot.state = RiskState.LOCK
        elif self.snapshot.current_drawdown >= self.snapshot.max_drawdown_limit:
            self.snapshot.state = RiskState.REDUCE
        elif self.snapshot.current_drawdown >= self.snapshot.max_drawdown_limit * 0.75:
            self.snapshot.state = RiskState.WATCH
        else:
            self.snapshot.state = RiskState.ACCEPT

        return self.snapshot.state

    def apply_stops_and_limits(
        self,
        entry_price: float,
        current_price: float,
        position_size: float,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.05,
    ) -> Dict[str, Any]:
        """Compute stop-loss and take-profit levels."""
        stop_loss = entry_price * (1 - stop_loss_pct)
        take_profit = entry_price * (1 + take_profit_pct)
        current_pnl_pct = (current_price - entry_price) / entry_price
        should_close = (
            current_price <= stop_loss
            or current_price >= take_profit
            or self.snapshot.state == RiskState.LOCK
        )

        return {
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "current_pnl_pct": round(current_pnl_pct, 4),
            "should_close": should_close,
            "close_reason": (
                "stop_loss" if current_price <= stop_loss
                else "take_profit" if current_price >= take_profit
                else "risk_lock" if self.snapshot.state == RiskState.LOCK
                else None
            ),
        }
