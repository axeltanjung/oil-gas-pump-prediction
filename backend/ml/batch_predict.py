"""
Batch prediction pipeline.

Scores the full telemetry dataset with the failure + RUL models and writes
predictions to `exports/batch_predictions.csv` and the SQLite `predictions`
table.

Run:
    python -m backend.ml.batch_predict
"""

from __future__ import annotations

import os
import sqlite3

import joblib
import numpy as np
import pandas as pd

from . import config, feature_engineering as fe, preprocessing


def run(output_csv: str | None = None) -> pd.DataFrame:
    config.ensure_dirs()
    df = preprocessing.basic_clean(preprocessing.load_dataset())
    df = fe.engineer(df)
    cols = fe.load_feature_meta()

    failure_model = joblib.load(config.FAILURE_MODEL_FILE)
    rul_model = joblib.load(config.RUL_MODEL_FILE)

    X = df[cols]
    df["failure_proba"] = failure_model.predict_proba(X)[:, 1]
    df["rul_pred_days"] = np.clip(rul_model.predict(X), 0, None)
    df["health_score"] = (1.0 - df["failure_proba"]).round(4)

    keep = [
        "timestamp",
        "pump_id",
        "failure_proba",
        "rul_pred_days",
        "health_score",
        "anomaly_score",
    ]
    result = df[keep].copy()

    out = output_csv or os.path.join(config.ROOT, "exports", "batch_predictions.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    result.to_csv(out, index=False)

    _write_predictions_table(result)
    print(f"[batch_predict] wrote {len(result):,} predictions -> {out}")
    return result


def _write_predictions_table(df: pd.DataFrame) -> None:
    conn = sqlite3.connect(config.SQLITE_PATH)
    try:
        out = df.copy()
        out["timestamp"] = out["timestamp"].astype(str)
        out.to_sql("predictions", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pred_pump ON predictions(pump_id)")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    run()
