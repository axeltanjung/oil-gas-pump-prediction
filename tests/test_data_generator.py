"""
Tests for the synthetic data generator (use a small config for speed).
"""
import os

os.environ.setdefault("N_PUMPS", "3")
os.environ.setdefault("N_HOURS", "300")

import pandas as pd  # noqa: E402

from data import data_generator as dg  # noqa: E402


def test_generate_shape_and_columns():
    df = dg.generate(write=False)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

    required = {
        "timestamp", "pump_id", "pressure", "vibration", "temperature", "rpm",
        "flow_rate", "operating_hours", "maintenance_history",
        "ambient_temperature", "power_consumption",
        "failure_within_7_days", "rul_days", "anomaly_score",
    }
    assert required.issubset(set(df.columns))


def test_targets_in_valid_ranges():
    df = dg.generate(write=False)
    assert set(df["failure_within_7_days"].unique()).issubset({0, 1})
    assert (df["rul_days"] >= 0).all()
    assert df["anomaly_score"].between(0, 1).all()


def test_multiple_pumps_and_failures():
    df = dg.generate(write=False)
    assert df["pump_id"].nunique() >= 2
    assert df["failure_event"].sum() > 0
