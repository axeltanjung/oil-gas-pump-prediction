# Architecture

## Components
1. **Data layer** — `data/data_generator.py` produces synthetic hourly telemetry
   for a fleet of pumps, persisted to CSV and SQLite (`telemetry`, `predictions`).
2. **ML layer** — `backend/ml/`
   - `preprocessing.py` → clean + load
   - `feature_engineering.py` → rolling stats, deltas, ratios
   - `train_failure.py` (XGBoost classifier + SHAP)
   - `train_rul.py` (XGBoost regressor)
   - `train_forecast.py` (PyTorch LSTM, sliding windows)
   - `mlflow_utils.py` → experiment tracking + registry
   - `batch_predict.py`, `retrain.py`, `drift_sim.py`
3. **API layer** — `backend/app/` (FastAPI)
   - `core/` config, logging, SQLite access
   - `services/` inference, alerts, PDF report
   - `api/routes/` health, predict, dashboard, pump, insights
4. **Presentation layer** — `frontend/` (React + Vite + Tailwind + Recharts)
   - Pages: Overview, Pump Detail, AI Insights, Alert Management

## Data flow
```
data_generator → CSV/SQLite ──► feature_engineering ──► train_* ──► models/ + MLflow
                                                                │
batch_predict ──► predictions table ◄───────────────────────────┘
                       │
FastAPI (reads telemetry + predictions) ──► REST ──► React dashboard
```

## Models
| Model | Type | Target |
|-------|------|--------|
| Failure classifier | XGBoost | `failure_within_7_days` |
| RUL regressor | XGBoost | `rul_days` |
| Degradation forecaster | PyTorch LSTM | next-step `health_index` |

## Deployment
`docker-compose.yml` builds three services: `backend` (FastAPI),
`frontend` (nginx-served React), and `mlflow` (tracking UI).
```

## Inference notes
On-demand predictions reconstruct engineered (rolling) features by pulling the
pump's recent history from SQLite; if no history exists, fallbacks are used
(rolling mean = current value, std = 0, delta = 0).
