"""
Inference service.

Lazily loads the trained models and exposes prediction helpers. For on-demand
single-reading predictions, engineered (rolling) features are reconstructed
using recent history from SQLite when available; otherwise sensible fallbacks
(rolling mean = current value, rolling std = 0, delta = 0) are used.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

import numpy as np
import pandas as pd

from backend.ml import config as mlcfg
from backend.ml import feature_engineering as fe

from ..core.db import query, table_exists
from ..core.logging_config import get_logger

log = get_logger("inference")

RAW = mlcfg.RAW_FEATURES


class ModelStore:
    """Holds lazily-loaded model artifacts."""

    def __init__(self) -> None:
        self._failure = None
        self._rul = None
        self._feature_cols: list[str] | None = None

    # ---- loaders ----
    @property
    def failure(self):
        if self._failure is None and os.path.exists(mlcfg.FAILURE_MODEL_FILE):
            import joblib

            self._failure = joblib.load(mlcfg.FAILURE_MODEL_FILE)
            log.info("Loaded failure model")
        return self._failure

    @property
    def rul(self):
        if self._rul is None and os.path.exists(mlcfg.RUL_MODEL_FILE):
            import joblib

            self._rul = joblib.load(mlcfg.RUL_MODEL_FILE)
            log.info("Loaded RUL model")
        return self._rul

    @property
    def feature_cols(self) -> list[str] | None:
        if self._feature_cols is None and os.path.exists(mlcfg.FEATURE_META_FILE):
            self._feature_cols = fe.load_feature_meta()
        return self._feature_cols

    def status(self) -> dict[str, bool]:
        return {
            "failure": os.path.exists(mlcfg.FAILURE_MODEL_FILE),
            "rul": os.path.exists(mlcfg.RUL_MODEL_FILE),
            "forecast": os.path.exists(mlcfg.FORECAST_MODEL_FILE),
        }


store = ModelStore()


# ---------------------------------------------------------------------------
# Feature reconstruction for a single reading
# ---------------------------------------------------------------------------
def _recent_history(pump_id: str, limit: int = 48) -> pd.DataFrame | None:
    if not table_exists("telemetry"):
        return None
    rows = query(
        "SELECT * FROM telemetry WHERE pump_id=? ORDER BY timestamp DESC LIMIT ?",
        (pump_id, limit),
    )
    if not rows:
        return None
    df = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def _build_feature_row(reading: dict) -> pd.DataFrame:
    """Return a single-row dataframe with all engineered feature columns."""
    cols = store.feature_cols
    hist = _recent_history(reading["pump_id"])

    base = {k: reading.get(k) for k in RAW}
    base["pump_id"] = reading["pump_id"]
    base["timestamp"] = pd.Timestamp.utcnow()

    if hist is not None and len(hist) > 1:
        hist_tail = hist[[*RAW, "pump_id", "timestamp"]].copy()
        new_row = pd.DataFrame([base])
        combined = pd.concat([hist_tail, new_row], ignore_index=True)
        eng = fe.engineer(combined)
        row = eng.iloc[[-1]].copy()
    else:
        # Fallback: engineer on a single row (rolling==value, std==0, delta==0)
        row = fe.engineer(pd.DataFrame([base])).iloc[[-1]].copy()

    if cols is not None:
        for c in cols:
            if c not in row.columns:
                row[c] = 0.0
        row = row[cols]
    return row.replace([np.inf, -np.inf], 0.0).fillna(0.0)


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------
def predict_failure(reading: dict) -> float:
    model = store.failure
    if model is None:
        raise RuntimeError("Failure model not trained. Run `python -m backend.ml.train_all`.")
    X = _build_feature_row(reading)
    return float(model.predict_proba(X)[0, 1])


def predict_rul(reading: dict) -> float:
    model = store.rul
    if model is None:
        raise RuntimeError("RUL model not trained. Run `python -m backend.ml.train_all`.")
    X = _build_feature_row(reading)
    return float(max(model.predict(X)[0], 0.0))


def predict_anomaly(reading: dict) -> float:
    """Heuristic anomaly score combining deviation of key sensors from history."""
    hist = _recent_history(reading["pump_id"], limit=200)
    score = 0.0
    if hist is not None and len(hist) > 5:
        for col, w in [("vibration", 0.4), ("temperature", 0.35), ("pressure", 0.25)]:
            mu, sigma = hist[col].mean(), hist[col].std() + 1e-6
            z = abs(reading[col] - mu) / sigma
            score += w * min(z / 3.0, 1.0)
    else:
        # Without history, derive from failure probability if model available.
        try:
            score = predict_failure(reading)
        except Exception:
            score = 0.0
    return float(min(max(score, 0.0), 1.0))


@lru_cache(maxsize=1)
def shap_drivers() -> list[dict]:
    """Top failure drivers from the persisted SHAP summary."""
    path = os.path.join(mlcfg.MODEL_DIR, "failure_shap.json")
    if not os.path.exists(path):
        path = os.path.join(mlcfg.MODEL_DIR, "failure_feature_importance.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)
