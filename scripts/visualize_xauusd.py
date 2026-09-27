"""Generate a price/volume chart and summary statistics for XAU/USD OHLCV data.

Usage:
    python scripts/visualize_xauusd.py
    python scripts/visualize_xauusd.py --input path/to/data.csv --output reports/xauusd.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {"time", "Open", "High", "Low", "Close", "Volume"}
DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "xauusd_test_data.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "reports" / "xauusd_overview.png"


def load_data(path: Path) -> pd.DataFrame:
    """Load and validate the OHLCV input file."""
    data = pd.read_csv(path, parse_dates=["time"])
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    data = data.sort_values("time").reset_index(drop=True)
    if data.empty:
        raise ValueError("The input data is empty")
    if data[list(REQUIRED_COLUMNS)].isnull().any().any():
        raise ValueError("The input data contains missing values")
    return data


def summary_statistics(data: pd.DataFrame) -> pd.Series:
    """Return useful scalar statistics for the displayed data."""
    close_return = (data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100
    hourly_returns = data["Close"].pct_change().dropna() * 100
    return pd.Series(
        {
            "rows": len(data),
            "start": data["time"].iloc[0],
            "end": data["time"].iloc[-1],
            "open_first": data["Open"].iloc[0],
            "close_last": data["Close"].iloc[-1],
            "high": data["High"].max(),
            "low": data["Low"].min(),
            "price_range": data["High"].max() - data["Low"].min(),
            "close_return_pct": close_return,
            "average_hourly_return_pct": hourly_returns.mean(),
            "hourly_return_volatility_pct": hourly_returns.std(),
            "average_volume": data["Volume"].mean(),
            "total_volume": data["Volume"].sum(),
            "bullish_candles": int((data["Close"] > data["Open"]).sum()),
            "bearish_candles": int((data["Close"] < data["Open"]).sum()),
        }
    )


def plot_overview(data: pd.DataFrame, output: Path) -> None:
    """Create a two-panel close-price and volume chart."""
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, (price_axis, volume_axis) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True, height_ratios=(3, 1), constrained_layout=True
    )

    price_axis.plot(data["time"], data["Close"], color="#1565c0", marker="o", label="Close")
    price_axis.fill_between(
        data["time"], data["Low"], data["High"], color="#90caf9", alpha=0.25, label="High–Low range"
    )
    price_axis.set_title("XAU/USD hourly price overview")
    price_axis.set_ylabel("Price")
    price_axis.grid(alpha=0.25)
    price_axis.legend(loc="best")

    volume_colors = ["#2e7d32" if close >= open_ else "#c62828" for close, open_ in zip(data["Close"], data["Open"])]
    volume_axis.bar(data["time"], data["Volume"], width=0.03, color=volume_colors)
    volume_axis.set_ylabel("Volume")
    volume_axis.set_xlabel("Time")
    volume_axis.grid(axis="y", alpha=0.25)
    volume_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    fig.savefig(output, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="OHLCV CSV file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PNG chart path")
    args = parser.parse_args()

    data = load_data(args.input)
    stats = summary_statistics(data)
    plot_overview(data, args.output)

    print(stats.to_string())
    print(f"\nChart written to: {args.output}")


if __name__ == "__main__":
    main()
