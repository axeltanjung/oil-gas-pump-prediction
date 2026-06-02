"""
Pydantic request/response models for the API.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
class SensorReading(BaseModel):
    """A single pump sensor reading used for on-demand prediction."""

    pump_id: str = Field(..., examples=["PUMP-001"])
    pressure: float = Field(..., examples=[52.3])
    vibration: float = Field(..., examples=[3.1])
    temperature: float = Field(..., examples=[68.5])
    rpm: float = Field(..., examples=[1490.0])
    flow_rate: float = Field(..., examples=[165.0])
    operating_hours: float = Field(..., examples=[12000.0])
    maintenance_history: int = Field(0, examples=[2])
    ambient_temperature: float = Field(25.0, examples=[27.0])
    power_consumption: float = Field(..., examples=[95.0])


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
class FailurePrediction(BaseModel):
    pump_id: str
    failure_probability: float
    failure_within_7_days: bool
    alert_level: str
    confidence: float


class RULPrediction(BaseModel):
    pump_id: str
    rul_days: float
    alert_level: str


class AnomalyPrediction(BaseModel):
    pump_id: str
    anomaly_score: float
    alert_level: str


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: dict[str, bool]
    database_ready: bool


class KpiSummary(BaseModel):
    total_pumps: int
    active_alerts: int
    high_risk_pumps: int
    average_health_score: float
    average_rul_days: float
    critical_pumps: int
    warning_pumps: int


class TrendPoint(BaseModel):
    timestamp: str
    value: float


class PumpDetail(BaseModel):
    pump_id: str
    latest: dict
    failure_probability: Optional[float] = None
    rul_days: Optional[float] = None
    anomaly_score: Optional[float] = None
    health_score: Optional[float] = None
    alert_level: str
    trends: dict[str, list[TrendPoint]]
    anomaly_timeline: list[TrendPoint]


class AlertItem(BaseModel):
    pump_id: str
    alert_level: str
    failure_probability: Optional[float] = None
    rul_days: Optional[float] = None
    anomaly_score: Optional[float] = None
    recommendation: str
