"""
Train all three models in sequence (data is generated if missing).

Run:
    python -m backend.ml.train_all
"""

from __future__ import annotations

import json

from . import config, mlflow_utils
from . import train_failure, train_forecast, train_rul


def main() -> dict:
    config.ensure_dirs()
    mlflow_utils.init_mlflow()

    print("=" * 60)
    print("Training Model 1 - Failure Classifier (XGBoost)")
    print("=" * 60)
    failure_metrics = train_failure.train()

    print("\n" + "=" * 60)
    print("Training Model 2 - RUL Regressor (XGBoost)")
    print("=" * 60)
    rul_metrics = train_rul.train()

    print("\n" + "=" * 60)
    print("Training Model 3 - Degradation Forecaster (PyTorch LSTM)")
    print("=" * 60)
    forecast_metrics = train_forecast.train()

    summary = {
        "failure": failure_metrics,
        "rul": rul_metrics,
        "forecast": forecast_metrics,
    }
    print("\n[train_all] DONE\n" + json.dumps(summary, indent=2, default=float))
    return summary


if __name__ == "__main__":
    main()
