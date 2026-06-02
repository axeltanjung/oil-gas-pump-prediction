"""
AI insights endpoint: SHAP drivers, feature importance, model metrics.
"""
from __future__ import annotations

import json
import os

from fastapi import APIRouter

from backend.ml import config as mlcfg

from ...services import inference

router = APIRouter(prefix="/insights", tags=["insights"])


def _read_json(path: str) -> list | dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


@router.get("/drivers")
def failure_drivers() -> list:
    """Top failure drivers (SHAP if available, else feature importance)."""
    return inference.shap_drivers()


@router.get("/feature-importance")
def feature_importance() -> dict:
    return {
        "failure": _read_json(os.path.join(mlcfg.MODEL_DIR, "failure_feature_importance.json")),
        "rul": _read_json(os.path.join(mlcfg.MODEL_DIR, "rul_feature_importance.json")),
    }


@router.get("/forecast-metrics")
def forecast_metrics() -> dict:
    return _read_json(os.path.join(mlcfg.MODEL_DIR, "forecast_metrics.json"))
