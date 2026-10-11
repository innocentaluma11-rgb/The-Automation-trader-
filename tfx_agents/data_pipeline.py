"""Market data ingestion and validation pipeline."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np


@dataclass
class OHLCV:
    """Open-High-Low-Close-Volume candlestick."""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass
class MarketDataCache:
    """In-memory cache of market data."""
    symbol: str
    candles: List[OHLCV] = field(default_factory=list)
    last_update: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_candle(self, candle: OHLCV) -> None:
        """Add a new candle to the cache."""
        self.candles.append(candle)
        self.last_update = datetime.utcnow()

    def get_latest(self, count: int = 1) -> List[OHLCV]:
        """Fetch the most recent candles."""
        return self.candles[-count:]

    def get_range(self, start: datetime, end: datetime) -> List[OHLCV]:
        """Fetch candles in a time range."""
        return [c for c in self.candles if start <= c.time <= end]


class DataPipeline:
    """Orchestrates data ingestion, validation, and distribution."""

    def __init__(self, symbol: str = "XAU/USD", cache_size: int = 1000):
        self.symbol = symbol
        self.cache_size = cache_size
        self.cache = MarketDataCache(symbol=symbol)
        self.validation_errors: List[str] = []

    def load_csv(self, path: Path) -> bool:
        """Load market data from a CSV file."""
        try:
            df = pd.read_csv(path, parse_dates=["time"])
            required = {"time", "open", "high", "low", "close", "volume"}
            if not required.issubset(df.columns):
                self.validation_errors.append(f"Missing columns: {required - set(df.columns)}")
                return False

            for _, row in df.iterrows():
                candle = OHLCV(
                    time=pd.Timestamp(row["time"]).to_pydatetime(),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
                self.cache.add_candle(candle)

            self.cache.metadata["source"] = "csv_file"
            self.cache.metadata["file"] = str(path)
            return True
        except Exception as e:
            self.validation_errors.append(f"CSV load error: {str(e)}")
            return False

    def generate_synthetic_data(self, bars: int = 100, start_price: float = 2341.0) -> None:
        """Generate synthetic OHLCV data for testing."""
        np.random.seed(42)
        current_time = datetime.utcnow() - timedelta(hours=bars)
        current_price = start_price

        for _ in range(bars):
            daily_return = np.random.normal(0.0003, 0.008)
            open_price = current_price
            close_price = open_price * (1 + daily_return)
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.003)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.003)))
            volume = np.random.uniform(50000, 200000)

            candle = OHLCV(
                time=current_time,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=round(volume, 0),
            )
            self.cache.add_candle(candle)
            current_price = close_price
            current_time += timedelta(hours=1)

        self.cache.metadata["source"] = "synthetic"
        self.cache.metadata["bars"] = bars

    def validate_candles(self) -> Dict[str, Any]:
        """Validate data integrity and detect anomalies."""
        if not self.cache.candles:
            return {"valid": False, "errors": ["No candles in cache"]}

        errors = []
        stats = {
            "count": len(self.cache.candles),
            "time_range": (
                self.cache.candles[0].time,
                self.cache.candles[-1].time,
            ),
            "gaps": 0,
            "anomalies": 0,
        }

        for i, candle in enumerate(self.cache.candles):
            if not (candle.low <= candle.close <= candle.high):
                errors.append(f"Invalid OHLC at index {i}: close not in range")
                stats["anomalies"] += 1
            if candle.volume < 0:
                errors.append(f"Negative volume at index {i}")
                stats["anomalies"] += 1

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "stats": stats,
        }

    def compute_indicators(self, window: int = 20) -> Dict[str, Any]:
        """Compute technical indicators over the cache."""
        if len(self.cache.candles) < window:
            return {"sma": None, "volatility": None, "volume_sma": None}

        closes = np.array([c.close for c in self.cache.candles[-window:]])
        volumes = np.array([c.volume for c in self.cache.candles[-window:]])

        sma = float(np.mean(closes))
        volatility = float(np.std(closes) / sma) if sma > 0 else 0.0
        volume_sma = float(np.mean(volumes))

        return {
            "sma_20": round(sma, 2),
            "volatility": round(volatility, 4),
            "volume_sma": round(volume_sma, 0),
            "latest_close": round(closes[-1], 2),
        }
