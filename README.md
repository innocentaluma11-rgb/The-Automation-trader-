# The-Automation-trader-
Automated trading research and testing pipeline for market data validation, strategy backtesting, risk analysis, and CI/CD workflows.

## XAU/USD visualization

Install the visualization dependencies and generate a price/volume chart plus printed summary statistics:

```bash
pip install -r requirements.txt
python scripts/visualize_xauusd.py
```

The script reads `xauusd_test_data.csv` by default and writes `reports/xauusd_overview.png`. Use `--input` and `--output` to select another CSV or output location:

```bash
python scripts/visualize_xauusd.py \
  --input xauusd_test_data.csv \
  --output reports/xauusd_overview.png
```

The chart contains the hourly close price with the high/low range and a color-coded volume panel (green for bullish candles, red for bearish candles). The console output includes the observed range, return, hourly volatility, volume, and candle counts.
