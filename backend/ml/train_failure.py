"""
Model 1 - Failure Classification (XGBoost).

Predicts P(failure within 7 days). Logs ROC AUC / Precision / Recall / F1 to
MLflow, generates SHAP explainability + feature-importance artifacts.

Run:
    python -m backend.ml.train_failure
"""
from __future__ import annotations

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from . import config, feature_engineering as fe, mlflow_utils, preprocessing


def _time_aware_split(df: pd.DataFrame, test_frac: float = 0.2):
    """Split chronologically per pump to avoid leakage."""
    df = df.sort_values(["pump_id", "timestamp"])
    train_parts, test_parts = [], []
    for _, grp in df.groupby("pump_id"):
        cut = int(len(grp) * (1 - test_frac))
        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])
    return pd.concat(train_parts), pd.concat(test_parts)


def train() -> dict:
    config.ensure_dirs()
    df = preprocessing.basic_clean(preprocessing.load_dataset())
    df = fe.engineer(df)
    cols = fe.feature_columns(df)
    fe.save_feature_meta(cols)

    train_df, test_df = _time_aware_split(df)
    X_train, y_train = train_df[cols], train_df[config.TARGET_FAILURE]
    X_test, y_test = test_df[cols], test_df[config.TARGET_FAILURE]

    pos = max(int(y_train.sum()), 1)
    neg = max(int((1 - y_train).sum()), 1)
    scale_pos_weight = neg / pos

    params = dict(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        n_jobs=-1,
        random_state=config.RANDOM_SEED,
    )

    with mlflow_utils.start_run("failure_xgb"):
        model = XGBClassifier(**params)
        model.fit(X_train, y_train)

        proba = model.predict_proba(X_test)[:, 1]
        preds = (proba >= 0.5).astype(int)
        metrics = {
            "roc_auc": roc_auc_score(y_test, proba),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "f1": f1_score(y_test, preds, zero_division=0),
            "accuracy": accuracy_score(y_test, preds),
        }
        mlflow_utils.log_params(params)
        mlflow_utils.log_metrics(metrics)

        joblib.dump(model, config.FAILURE_MODEL_FILE)
        _export_feature_importance(model, cols)
        _export_shap(model, X_test.sample(min(2000, len(X_test)), random_state=1), cols)

        mlflow_utils.log_artifact(config.FAILURE_MODEL_FILE)
        mlflow_utils.log_sklearn_model(model, "failure_model", config.REG_FAILURE)

    print("[train_failure] metrics:", json.dumps({k: round(v, 4) for k, v in metrics.items()}))
    return metrics


def _export_feature_importance(model, cols: list[str]) -> None:
    imp = pd.DataFrame(
        {"feature": cols, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    out = os.path.join(config.MODEL_DIR, "failure_feature_importance.json")
    imp.head(25).to_json(out, orient="records")
    mlflow_utils.log_artifact(out)


def _export_shap(model, X_sample: pd.DataFrame, cols: list[str]) -> None:
    """Compute mean |SHAP| per feature and persist for the AI Insights page."""
    try:
        import shap

        explainer = shap.TreeExplainer(model)
        vals = explainer.shap_values(X_sample)
        if isinstance(vals, list):
            vals = vals[-1]
        mean_abs = np.abs(vals).mean(axis=0)
        shap_df = pd.DataFrame({"feature": cols, "mean_abs_shap": mean_abs})
        shap_df.sort_values("mean_abs_shap", ascending=False, inplace=True)
        out = os.path.join(config.MODEL_DIR, "failure_shap.json")
        shap_df.head(25).to_json(out, orient="records")
        mlflow_utils.log_artifact(out)
    except Exception as exc:  # SHAP optional / heavy
        print(f"[train_failure] SHAP skipped: {exc}")


if __name__ == "__main__":
    train()
