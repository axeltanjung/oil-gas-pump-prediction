"""
Prediction endpoints: failure, RUL, anomaly.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...core.config import settings
from ...schemas.io import (
    AnomalyPrediction,
    FailurePrediction,
    RULPrediction,
    SensorReading,
)
from ...services import alerts, inference

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/failure", response_model=FailurePrediction)
def predict_failure(reading: SensorReading) -> FailurePrediction:
    try:
        prob = inference.predict_failure(reading.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    level = alerts.failure_level(prob)
    confidence = abs(prob - 0.5) * 2  # distance from decision boundary
    return FailurePrediction(
        pump_id=reading.pump_id,
        failure_probability=round(prob, 4),
        failure_within_7_days=prob >= 0.5,
        alert_level=level,
        confidence=round(confidence, 4),
    )


@router.post("/rul", response_model=RULPrediction)
def predict_rul(reading: SensorReading) -> RULPrediction:
    try:
        rul = inference.predict_rul(reading.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return RULPrediction(
        pump_id=reading.pump_id,
        rul_days=round(rul, 2),
        alert_level=alerts.rul_level(rul),
    )


@router.post("/anomaly", response_model=AnomalyPrediction)
def predict_anomaly(reading: SensorReading) -> AnomalyPrediction:
    score = inference.predict_anomaly(reading.model_dump())
    return AnomalyPrediction(
        pump_id=reading.pump_id,
        anomaly_score=round(score, 4),
        alert_level=alerts.anomaly_level(score),
    )
