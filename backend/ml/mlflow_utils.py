"""
MLflow helpers: configure tracking, start runs, register models.
Falls back gracefully (no crash) if MLflow is unavailable.
"""
from __future__ import annotations

import contextlib
from typing import Iterator

from . import config

try:
    import mlflow

    _HAS_MLFLOW = True
except Exception:  # pragma: no cover
    _HAS_MLFLOW = False


def init_mlflow() -> None:
    if not _HAS_MLFLOW:
        return
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.MLFLOW_EXPERIMENT)


@contextlib.contextmanager
def start_run(run_name: str) -> Iterator[object]:
    """Context manager that yields an MLflow run (or a no-op stub)."""
    if not _HAS_MLFLOW:
        yield None
        return
    init_mlflow()
    with mlflow.start_run(run_name=run_name) as run:
        yield run


def log_params(params: dict) -> None:
    if _HAS_MLFLOW:
        mlflow.log_params(params)


def log_metrics(metrics: dict) -> None:
    if _HAS_MLFLOW:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()})


def log_artifact(path: str) -> None:
    if _HAS_MLFLOW:
        mlflow.log_artifact(path)


def log_sklearn_model(model, artifact_path: str, registered_name: str | None = None) -> None:
    if not _HAS_MLFLOW:
        return
    try:
        mlflow.sklearn.log_model(
            model, artifact_path=artifact_path, registered_model_name=registered_name
        )
    except Exception as exc:  # registry may be unavailable on file store
        print(f"[mlflow] model registry skipped: {exc}")
