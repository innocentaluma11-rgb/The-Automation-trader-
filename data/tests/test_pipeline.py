import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).parent / "xauusd_test_data.csv"


def load_data():
    return pd.read_csv(DATA_PATH)


def test_data_is_not_empty():
    assert not load_data().empty


def test_required_columns_exist():
    data = load_data()
    assert {"time", "Open", "High", "Low", "Close", "Volume"}.issubset(data.columns)


def test_data_has_no_missing_values():
    assert not load_data().isnull().any().any()


def test_high_is_greater_than_low():
    data = load_data()
    assert (data["High"] >= data["Low"]).all()


def test_close_is_within_high_low_range():
    data = load_data()
    assert (data["Close"] >= data["Low"]).all()
    assert (data["Close"] <= data["High"]).all()


def test_prices_and_volume_are_non_negative():
    data = load_data()
    assert (data[["Open", "High", "Low", "Close"]] > 0).all().all()
    assert (data["Volume"] >= 0).all()
