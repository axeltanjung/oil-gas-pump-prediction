"""
Per-pump detail endpoint: telemetry trends, latest predictions, anomaly
timeline, plus a downloadable PDF maintenance report.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from ...core.db import query, table_exists
from ...schemas.io import PumpDetail, TrendPoint
from ...services import alerts, inference
from ...services.report import build_pump_report

router = APIRouter(prefix="/pump", tags=["pump"])

TREND_COLS = [
    "pressure",
    "vibration",
    "temperature",
    "rpm",
    "flow_rate",
    "power_consumption",
]


def _build_detail(pump_id: str, points: int) -> dict:
    if not table_exists("telemetry"):
        raise HTTPException(
            status_code=503, detail="Telemetry table not found. Generate data first."
        )

    rows = query(
        "SELECT * FROM telemetry WHERE pump_id=? ORDER BY timestamp DESC LIMIT ?",
        (pump_id, points),
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Pump {pump_id} not found")
    rows = rows[::-1]  # chronological
    latest = rows[-1]

    trends: dict[str, list[TrendPoint]] = {}
    for col in TREND_COLS:
        trends[col] = [TrendPoint(timestamp=r["timestamp"], value=r[col]) for r in rows]

    anomaly_timeline = [
        TrendPoint(timestamp=r["timestamp"], value=r.get("anomaly_score", 0.0))
        for r in rows
    ]

    # Latest predictions (prefer batch predictions table, else compute on the fly)
    failure_proba = rul_days = anomaly = health = None
    if table_exists("predictions"):
        pred = query(
            "SELECT * FROM predictions WHERE pump_id=? ORDER BY timestamp DESC LIMIT 1",
            (pump_id,),
        )
        if pred:
            p = pred[0]
            failure_proba = round(p.get("failure_proba", 0.0), 4)
            rul_days = round(p.get("rul_pred_days", 0.0), 2)
            anomaly = round(p.get("anomaly_score", 0.0), 4)
            health = round(p.get("health_score", 0.0), 4)

    if failure_proba is None:
        try:
            reading = {k: latest[k] for k in inference.RAW}
            reading["pump_id"] = pump_id
            failure_proba = round(inference.predict_failure(reading), 4)
            rul_days = round(inference.predict_rul(reading), 2)
            anomaly = round(latest.get("anomaly_score", 0.0), 4)
            health = round(1.0 - failure_proba, 4)
        except Exception:
            pass

    level = alerts.combine(
        alerts.failure_level(failure_proba or 0.0),
        alerts.rul_level(rul_days if rul_days is not None else 9999),
        alerts.anomaly_level(anomaly or 0.0),
    )

    return {
        "pump_id": pump_id,
        "latest": latest,
        "failure_probability": failure_proba,
        "rul_days": rul_days,
        "anomaly_score": anomaly,
        "health_score": health,
        "alert_level": level,
        "trends": trends,
        "anomaly_timeline": anomaly_timeline,
    }


@router.get("/{pump_id}", response_model=PumpDetail)
def pump_detail(pump_id: str, points: int = Query(300, ge=10, le=2000)) -> PumpDetail:
    return PumpDetail(**_build_detail(pump_id, points))


@router.get("/{pump_id}/report")
def pump_report(pump_id: str):
    detail = _build_detail(pump_id, points=50)
    path = build_pump_report(pump_id, detail)
    return FileResponse(
        path, media_type="application/pdf", filename=f"report_{pump_id}.pdf"
    )


@router.get("")
def list_pumps() -> list[str]:
    if not table_exists("telemetry"):
        raise HTTPException(status_code=503, detail="Telemetry table not found.")
    rows = query("SELECT DISTINCT pump_id FROM telemetry ORDER BY pump_id")
    return [r["pump_id"] for r in rows]
