"""Real-time monitoring and alerting for system health and P&L."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class AlertSeverity(str, Enum):
    """Alert criticality level."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """System or trading alert."""
    timestamp: datetime
    severity: AlertSeverity
    component: str  # e.g., "data_pipeline", "execution", "risk"
    message: str
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "component": self.component,
            "message": self.message,
            "context": self.context,
        }


@dataclass
class PerformanceMetrics:
    """Aggregated performance snapshot."""
    timestamp: datetime
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    gross_pnl: float = 0.0
    gross_pnl_pct: float = 0.0
    avg_latency_ms: float = 0.0
    data_quality_score: float = 1.0
    uptime_pct: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "gross_pnl": round(self.gross_pnl, 2),
            "gross_pnl_pct": round(self.gross_pnl_pct, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "data_quality_score": round(self.data_quality_score, 3),
            "uptime_pct": round(self.uptime_pct, 1),
        }


class PerformanceMonitor:
    """Tracks system health, latency, P&L, and generates alerts."""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_metrics = PerformanceMetrics(timestamp=datetime.utcnow())
        self.latencies: List[float] = []

    def record_latency(self, latency_ms: float) -> None:
        """Record execution latency for an operation."""
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies = self.latencies[-1000:]

    def record_trade(self, pnl: float, side: str) -> None:
        """Record a closed trade's P&L."""
        self.current_metrics.total_trades += 1
        if pnl > 0:
            self.current_metrics.winning_trades += 1
        else:
            self.current_metrics.losing_trades += 1
        self.current_metrics.gross_pnl += pnl

    def add_alert(
        self,
        severity: AlertSeverity,
        component: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Generate an alert."""
        alert = Alert(
            timestamp=datetime.utcnow(),
            severity=severity,
            component=component,
            message=message,
            context=context or {},
        )
        self.alerts.append(alert)

    def check_anomalies(self, current_price: float, expected_price: float, tolerance_pct: float = 5.0) -> None:
        """Detect price anomalies."""
        deviation = abs(current_price - expected_price) / expected_price * 100 if expected_price > 0 else 0.0
        if deviation > tolerance_pct:
            self.add_alert(
                AlertSeverity.WARNING,
                "data_pipeline",
                f"Price deviation detected: {deviation:.2f}% from expected",
                {"current": current_price, "expected": expected_price, "deviation_pct": deviation},
            )

    def generate_report(self) -> Dict[str, Any]:
        """Generate a performance and health report."""
        avg_latency = np.mean(self.latencies) if self.latencies else 0.0
        data_quality = 1.0 - min(len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]) / 10.0, 1.0)

        report = PerformanceMetrics(
            timestamp=datetime.utcnow(),
            total_trades=self.current_metrics.total_trades,
            winning_trades=self.current_metrics.winning_trades,
            losing_trades=self.current_metrics.losing_trades,
            gross_pnl=self.current_metrics.gross_pnl,
            gross_pnl_pct=(
                self.current_metrics.gross_pnl / 100000.0 * 100  # assuming 100k capital
            ),
            avg_latency_ms=avg_latency,
            data_quality_score=data_quality,
            uptime_pct=100.0,
        )
        self.metrics_history.append(report)
        return report.to_dict()
