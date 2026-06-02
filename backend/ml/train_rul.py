"""
Model 2 - Remaining Useful Life (RUL) prediction (XGBoost Regressor).

Logs RMSE / MAE / R2 to MLflow.

Run:
    python -m backend.ml.train_rul
"""
from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from . import config, feature_engineering as fe, mlflow_utils, preprocessing
from .train_failure import _time_aware_split


def train() -> dict:
    config.ensure_dirs()
    df = preprocessing.basic_clean(preprocessing.load_dataset())
    df = fe.engineer(df)
    cols = fe.feature_columns(df)

    train_df, test_df = _time_aware_split(df)
    X_train, y_train = train_df[cols], train_df[config.TARGET_RUL]
    X_test, y_test = test_df[cols], test_df[config.TARGET_RUL]

    params = dict(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        n_jobs=-1,
        random_state=config.RANDOM_SEED,
    )

    with mlflow_utils.start_run("rul_xgb"):
        model = XGBRegressor(**params)
        model.fit(X_train, y_train)

        preds = np.clip(model.predict(X_test), 0, None)
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        metrics = {
            "rmse": rmse,
            "mae": float(mean_absolute_error(y_test, preds)),
            "r2": float(r2_score(y_test, preds)),
        }
        mlflow_utils.log_params(params)
        mlflow_utils.log_metrics(metrics)

        joblib.dump(model, config.RUL_MODEL_FILE)
        _export_importance(model, cols)
        mlflow_utils.log_artifact(config.RUL_MODEL_FILE)
        mlflow_utils.log_sklearn_model(model, "rul_model", config.REG_RUL)

    print("[train_rul] metrics:", json.dumps({k: round(v, 4) for k, v in metrics.items()}))
    return metrics


def _export_importance(model, cols: list[str]) -> None:
    import os

    imp = pd.DataFrame(
        {"feature": cols, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    out = os.path.join(config.MODEL_DIR, "rul_feature_importance.json")
    imp.head(25).to_json(out, orient="records")
    mlflow_utils.log_artifact(out)


if __name__ == "__main__":
    train()
