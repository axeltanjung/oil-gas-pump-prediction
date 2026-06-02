"""
Shared ML configuration: paths, feature lists, model names, hyperparameters.
"""
from __future__ import annotations

import os

# ---- Paths ----
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(ROOT, "data"))
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(ROOT, "models"))
CSV_PATH = os.path.join(DATA_DIR, "pump_telemetry.csv")
SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(DATA_DIR, "pumps.db"))

# ---- MLflow ----
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", os.path.join(ROOT, "mlflow", "mlruns"))
MLFLOW_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT", "oil_gas_pump_prediction")

# ---- Targets / horizon ----
FAILURE_HORIZON_DAYS = int(os.getenv("FAILURE_HORIZON_DAYS", "7"))

# ---- Raw sensor columns ----
RAW_FEATURES = [
    "pressure",
    "vibration",
    "temperature",
    "rpm",
    "flow_rate",
    "operating_hours",
    "maintenance_history",
    "ambient_temperature",
    "power_consumption",
]

# ---- Targets ----
TARGET_FAILURE = "failure_within_7_days"
TARGET_RUL = "rul_days"
TARGET_HEALTH = "health_index"
TARGET_ANOMALY = "anomaly_score"

# ---- Model artifact names ----
FAILURE_MODEL_FILE = os.path.join(MODEL_DIR, "failure_xgb.joblib")
RUL_MODEL_FILE = os.path.join(MODEL_DIR, "rul_xgb.joblib")
FORECAST_MODEL_FILE = os.path.join(MODEL_DIR, "forecast_lstm.pt")
FEATURE_META_FILE = os.path.join(MODEL_DIR, "feature_meta.json")
SCALER_FILE = os.path.join(MODEL_DIR, "lstm_scaler.joblib")

# ---- Registered model names (MLflow registry) ----
REG_FAILURE = "pump_failure_classifier"
REG_RUL = "pump_rul_regressor"
REG_FORECAST = "pump_degradation_lstm"

# ---- LSTM ----
LSTM_SEQUENCE_LEN = int(os.getenv("LSTM_SEQUENCE_LEN", "48"))
LSTM_EPOCHS = int(os.getenv("LSTM_EPOCHS", "15"))
LSTM_HIDDEN = 64
LSTM_LAYERS = 2
LSTM_LR = 1e-3
LSTM_BATCH = 256

# ---- Alert thresholds (shared with backend services) ----
FAILURE_PROB_WARNING = 0.40
FAILURE_PROB_CRITICAL = 0.70
RUL_WARNING_DAYS = 14
RUL_CRITICAL_DAYS = 5
ANOMALY_WARNING = 0.50
ANOMALY_CRITICAL = 0.75

RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))


def ensure_dirs() -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MLFLOW_TRACKING_URI, exist_ok=True)
