"""
Tests for feature engineering and alert logic.
"""

import os

os.environ.setdefault("N_PUMPS", "3")
os.environ.setdefault("N_HOURS", "300")

from backend.app.services import alerts  # noqa: E402
from backend.ml import feature_engineering as fe  # noqa: E402
from data import data_generator as dg  # noqa: E402


def test_engineer_adds_rolling_features():
    df = dg.generate(write=False)
    eng = fe.engineer(df)
    assert "vibration_roll_mean_6" in eng.columns
    assert "temp_over_ambient" in eng.columns
    assert "power_per_flow" in eng.columns
    assert eng.isna().sum().sum() == 0


def test_feature_columns_excludes_targets():
    df = dg.generate(write=False)
    eng = fe.engineer(df)
    cols = fe.feature_columns(eng)
    for t in [
        "failure_within_7_days",
        "rul_days",
        "anomaly_score",
        "pump_id",
        "timestamp",
    ]:
        assert t not in cols


def test_alert_levels():
    assert alerts.failure_level(0.9) == alerts.CRITICAL
    assert alerts.failure_level(0.5) == alerts.WARNING
    assert alerts.failure_level(0.1) == alerts.NORMAL
    assert alerts.rul_level(2) == alerts.CRITICAL
    assert (
        alerts.combine(alerts.NORMAL, alerts.WARNING, alerts.CRITICAL)
        == alerts.CRITICAL
    )
