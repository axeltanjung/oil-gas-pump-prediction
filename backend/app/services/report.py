"""
PDF maintenance report generation (reportlab).
"""

from __future__ import annotations

import os
from datetime import datetime

from ..core.config import settings


def build_pump_report(pump_id: str, detail: dict) -> str:
    """Render a one-page PDF maintenance report; return the file path."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    os.makedirs(settings.exports_dir, exist_ok=True)
    out = os.path.join(settings.exports_dir, f"maintenance_report_{pump_id}.pdf")

    c = canvas.Canvas(out, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    c.setFillColor(colors.HexColor("#0EA5E9"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, y, "Pump Maintenance Report")
    y -= 0.7 * cm
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M UTC}")
    y -= 1.0 * cm

    def line(label: str, value: str) -> None:
        nonlocal y
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, f"{label}:")
        c.setFont("Helvetica", 11)
        c.drawString(7 * cm, y, str(value))
        y -= 0.6 * cm

    line("Pump ID", pump_id)
    line("Alert Level", detail.get("alert_level", "N/A"))
    fp = detail.get("failure_probability")
    line("Failure Probability", f"{fp:.1%}" if fp is not None else "N/A")
    rul = detail.get("rul_days")
    line("Remaining Useful Life", f"{rul:.1f} days" if rul is not None else "N/A")
    anom = detail.get("anomaly_score")
    line("Anomaly Score", f"{anom:.2f}" if anom is not None else "N/A")
    health = detail.get("health_score")
    line("Health Score", f"{health:.1%}" if health is not None else "N/A")

    y -= 0.4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Latest Sensor Readings")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    for k, v in (detail.get("latest") or {}).items():
        if k in ("timestamp", "pump_id"):
            continue
        c.drawString(2.3 * cm, y, f"- {k}: {v}")
        y -= 0.45 * cm
        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm

    c.showPage()
    c.save()
    return out
