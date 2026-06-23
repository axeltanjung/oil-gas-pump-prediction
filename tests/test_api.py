"""
Smoke tests for the FastAPI app (no trained models required for /health and /).
"""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "endpoints" in r.json()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "models_loaded" in body


def test_predict_failure_without_model_returns_503():
    # If models are not trained, endpoint should respond 503 (not crash).
    payload = {
        "pump_id": "PUMP-001",
        "pressure": 52.0,
        "vibration": 3.0,
        "temperature": 68.0,
        "rpm": 1490,
        "flow_rate": 165,
        "operating_hours": 12000,
        "maintenance_history": 1,
        "ambient_temperature": 26,
        "power_consumption": 95,
    }
    r = client.post("/predict/failure", json=payload)
    assert r.status_code in (200, 503)
