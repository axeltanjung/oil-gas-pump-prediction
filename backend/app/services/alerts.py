"""
Alert-level logic and maintenance recommendations shared across endpoints.
"""
from __future__ import annotations

from ..core.config import settings

NORMAL = "Normal"
WARNING = "Warning"
CRITICAL = "Critical"


def failure_level(prob: float) -> str:
    if prob >= settings.failure_prob_critical:
        return CRITICAL
    if prob >= settings.failure_prob_warning:
        return WARNING
    return NORMAL


def rul_level(rul_days: float) -> str:
    if rul_days <= settings.rul_critical_days:
        return CRITICAL
    if rul_days <= settings.rul_warning_days:
        return WARNING
    return NORMAL


def anomaly_level(score: float) -> str:
    if score >= settings.anomaly_critical:
        return CRITICAL
    if score >= settings.anomaly_warning:
        return WARNING
    return NORMAL


_SEVERITY = {NORMAL: 0, WARNING: 1, CRITICAL: 2}


def combine(*levels: str) -> str:
    """Return the most severe level among the provided ones."""
    best = NORMAL
    for lv in levels:
        if _SEVERITY.get(lv, 0) > _SEVERITY[best]:
            best = lv
    return best


def recommendation(level: str, rul_days: float | None = None) -> str:
    if level == CRITICAL:
        base = "Immediate inspection required; schedule shutdown/maintenance within 48h."
    elif level == WARNING:
        base = "Plan maintenance; increase monitoring frequency."
    else:
        base = "Operating normally; continue routine monitoring."
    if rul_days is not None and level != NORMAL:
        base += f" Estimated RUL ~{rul_days:.1f} days."
    return base
