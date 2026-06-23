"""
Feature engineering for the tabular models (failure classifier + RUL regressor).

Adds rolling statistics, deltas, and ratios per pump. The exact engineered
feature list is persisted to `feature_meta.json` so inference can rebuild the
same columns from a single reading + recent history.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import config

ROLL_WINDOWS = [6, 24]  # hours
ROLL_COLS = [
    "pressure",
    "vibration",
    "temperature",
    "rpm",
    "flow_rate",
    "power_consumption",
]


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Create engineered features. Operates per pump to avoid leakage across assets."""
    df = df.sort_values(["pump_id", "timestamp"]).copy()
    g = df.groupby("pump_id", group_keys=False)

    for col in ROLL_COLS:
        for w in ROLL_WINDOWS:
            df[f"{col}_roll_mean_{w}"] = g[col].transform(
                lambda s: s.rolling(w, min_periods=1).mean()
            )
            df[f"{col}_roll_std_{w}"] = g[col].transform(
                lambda s: s.rolling(w, min_periods=1).std().fillna(0.0)
            )
        # first difference (rate of change)
        df[f"{col}_delta"] = g[col].transform(lambda s: s.diff().fillna(0.0))

    # Physics-inspired ratios
    df["power_per_flow"] = df["power_consumption"] / (df["flow_rate"].abs() + 1e-3)
    df["temp_over_ambient"] = df["temperature"] - df["ambient_temperature"]
    df["vib_temp_product"] = df["vibration"] * df["temperature"]

    df = df.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return df


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the model input columns (raw + engineered, excluding targets/ids)."""
    exclude = {
        "timestamp",
        "pump_id",
        config.TARGET_FAILURE,
        config.TARGET_RUL,
        config.TARGET_HEALTH,
        config.TARGET_ANOMALY,
        "failure_event",
    }
    return [c for c in df.columns if c not in exclude]


def save_feature_meta(columns: list[str]) -> None:
    config.ensure_dirs()
    with open(config.FEATURE_META_FILE, "w") as f:
        json.dump({"feature_columns": columns}, f, indent=2)


def load_feature_meta() -> list[str]:
    with open(config.FEATURE_META_FILE) as f:
        return json.load(f)["feature_columns"]
