"""
Data loading & preprocessing utilities.
"""
from __future__ import annotations

import os

import pandas as pd

from . import config


def load_dataset(csv_path: str | None = None) -> pd.DataFrame:
    """Load the telemetry dataset, generating it on the fly if missing."""
    path = csv_path or config.CSV_PATH
    if not os.path.exists(path):
        # Lazy generation so the pipeline is runnable end-to-end.
        from data.data_generator import generate

        return generate(write=True)
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Sort, drop dupes, forward-fill minor gaps within each pump."""
    df = df.sort_values(["pump_id", "timestamp"]).copy()
    df = df.drop_duplicates(subset=["pump_id", "timestamp"])
    df[config.RAW_FEATURES] = (
        df.groupby("pump_id")[config.RAW_FEATURES].ffill().bfill()
    )
    return df.reset_index(drop=True)
