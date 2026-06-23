"""
Dashboard summary endpoint + alerts list.

Aggregates the latest batch predictions per pump. Run
`python -m backend.ml.batch_predict` to populate the `predictions` table.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...core.db import query, table_exists
from ...schemas.io import AlertItem, KpiSummary
from ...services import alerts

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_LATEST_PRED_SQL = """
SELECT p.*
FROM predictions p
JOIN (
    SELECT pump_id, MAX(timestamp) AS mx
    FROM predictions GROUP BY pump_id
) last ON p.pump_id = last.pump_id AND p.timestamp = last.mx
"""


def _latest_predictions() -> list[dict]:
    if not table_exists("predictions"):
        raise HTTPException(
            status_code=503,
            detail="No predictions found. Run `python -m backend.ml.batch_predict`.",
        )
    return query(_LATEST_PRED_SQL)


def _level_for(row: dict) -> str:
    return alerts.combine(
        alerts.failure_level(row.get("failure_proba", 0.0)),
        alerts.rul_level(row.get("rul_pred_days", 9999)),
        alerts.anomaly_level(row.get("anomaly_score", 0.0)),
    )


@router.get("/summary", response_model=KpiSummary)
def summary() -> KpiSummary:
    rows = _latest_predictions()
    total = len(rows)
    levels = [_level_for(r) for r in rows]
    critical = sum(1 for lv in levels if lv == alerts.CRITICAL)
    warning = sum(1 for lv in levels if lv == alerts.WARNING)
    high_risk = sum(1 for r in rows if r.get("failure_proba", 0) >= 0.5)
    avg_health = sum(r.get("health_score", 0.0) for r in rows) / total if total else 0.0
    avg_rul = sum(r.get("rul_pred_days", 0.0) for r in rows) / total if total else 0.0

    return KpiSummary(
        total_pumps=total,
        active_alerts=critical + warning,
        high_risk_pumps=high_risk,
        average_health_score=round(avg_health, 4),
        average_rul_days=round(avg_rul, 2),
        critical_pumps=critical,
        warning_pumps=warning,
    )


@router.get("/alerts", response_model=list[AlertItem])
def alert_list() -> list[AlertItem]:
    rows = _latest_predictions()
    items: list[AlertItem] = []
    for r in rows:
        level = _level_for(r)
        if level == alerts.NORMAL:
            continue
        items.append(
            AlertItem(
                pump_id=r["pump_id"],
                alert_level=level,
                failure_probability=round(r.get("failure_proba", 0.0), 4),
                rul_days=round(r.get("rul_pred_days", 0.0), 2),
                anomaly_score=round(r.get("anomaly_score", 0.0), 4),
                recommendation=alerts.recommendation(level, r.get("rul_pred_days")),
            )
        )
    order = {alerts.CRITICAL: 0, alerts.WARNING: 1}
    items.sort(key=lambda x: order.get(x.alert_level, 2))
    return items


@router.get("/risk-heatmap")
def risk_heatmap() -> list[dict]:
    """Per-pump risk cells for the overview heatmap."""
    rows = _latest_predictions()
    return [
        {
            "pump_id": r["pump_id"],
            "failure_proba": round(r.get("failure_proba", 0.0), 4),
            "rul_days": round(r.get("rul_pred_days", 0.0), 2),
            "anomaly_score": round(r.get("anomaly_score", 0.0), 4),
            "alert_level": _level_for(r),
        }
        for r in rows
    ]
