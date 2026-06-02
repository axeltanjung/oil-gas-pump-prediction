# Oil & Gas Pump Failure Prediction System

> Production-style, end-to-end predictive maintenance platform for industrial Oil & Gas pumps.
> Predicts **failure probability**, **Remaining Useful Life (RUL)**, and **anomaly/early-warning status**
> from simulated sensor telemetry — with a modern dark industrial dashboard.

[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)]()
[![React](https://img.shields.io/badge/React-Vite-61dafb)]()
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED)]()
[![MLflow](https://img.shields.io/badge/MLflow-2.13-0194E2)]()

---

## Table of Contents
1. [Architecture](#architecture)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Quick Start (Docker)](#quick-start-docker)
5. [Local Development (no Docker)](#local-development-no-docker)
6. [ML Pipeline & Models](#ml-pipeline--models)
7. [MLflow](#mlflow)
8. [API Documentation](#api-documentation)
9. [Dashboard](#dashboard)
10. [Extra Features](#extra-features)
11. [Screenshots](#screenshots)
12. [Future Improvements](#future-improvements)

---

## Architecture

```
                         ┌──────────────────────────────────────────────┐
                         │              React + Vite Dashboard            │
                         │  Overview · Pump Detail · AI Insights · Alerts │
                         └───────────────────────┬──────────────────────┘
                                                 │  REST (Axios)
                                                 ▼
                         ┌──────────────────────────────────────────────┐
                         │                FastAPI Backend                 │
                         │  /health /predict/* /dashboard/summary /pump   │
                         │  Pydantic · Logging · Error handling           │
                         └───────┬───────────────┬───────────────┬───────┘
                                 │               │               │
                     ┌───────────▼──┐  ┌─────────▼────────┐  ┌───▼────────────┐
                     │ Model Registry│  │   SQLite (telemetry│  │  Services       │
                     │ XGB-failure   │  │   + predictions)   │  │ alerts / report │
                     │ XGB-RUL       │  └──────────────────┘  │ drift / batch   │
                     │ LSTM-forecast │                         └────────────────┘
                     └───────▲───────┘
                             │  artifacts + metrics
                     ┌───────┴───────────────────────────┐
                     │           MLflow Tracking          │
                     │  experiments · metrics · registry  │
                     └───────▲───────────────────────────┘
                             │
                     ┌───────┴───────────┐
                     │ Synthetic Data Gen │  data_generator.py → CSV → SQLite
                     │ (degradation model)│
                     └────────────────────┘
```

---

## Features
- **Synthetic industrial dataset** (100k+ rows): multi-pump hourly telemetry with realistic degradation, sensor noise, overheating, cavitation, vibration spikes, gradual wear, and sudden failures.
- **3 ML models**: XGBoost failure classifier (+ SHAP), XGBoost RUL regressor, PyTorch LSTM degradation forecaster.
- **MLflow** experiment tracking, artifact logging, and model registry.
- **FastAPI** backend with Pydantic validation, Swagger docs, logging, modular services.
- **React + Vite + Tailwind** dark industrial dashboard with Recharts visualizations.
- **Docker Compose** one-command deployment (backend + frontend + MLflow UI).
- **Extras**: drift simulation, retraining, batch prediction, CSV export, PDF maintenance report.

---

## Project Structure
```
oil-gas-pump-prediction/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint
│   │   ├── core/                  # config, logging, db (SQLite)
│   │   ├── schemas/               # Pydantic models
│   │   ├── services/              # inference, alerts, report, drift
│   │   └── api/routes/            # health, predict, dashboard, pump
│   └── ml/
│       ├── preprocessing.py
│       ├── feature_engineering.py
│       ├── mlflow_utils.py
│       ├── train_failure.py       # Model 1 - XGBoost + SHAP
│       ├── train_rul.py           # Model 2 - XGBoost regressor
│       ├── train_forecast.py      # Model 3 - PyTorch LSTM
│       ├── train_all.py
│       ├── batch_predict.py
│       ├── retrain.py
│       └── drift_sim.py
├── data/
│   ├── data_generator.py
│   └── pump_telemetry.csv         # (generated)
├── models/                        # (generated artifacts)
├── notebooks/
├── mlflow/
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
├── docs/
├── screenshots/
├── tests/
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Quick Start (Docker)

```bash
# 1. Configure environment
cp .env.example .env

# 2. (One-time) Generate data and train models INSIDE the backend image,
#    or run locally first (see below) so artifacts exist in ./data and ./models.

# 3. Launch everything
docker-compose up --build
```

| Service     | URL                       |
|-------------|---------------------------|
| Dashboard   | http://localhost:3000     |
| API + Swagger | http://localhost:8000/docs |
| MLflow UI   | http://localhost:5000     |

> **Note:** model artifacts are produced by the training scripts. Run the
> training step first (locally or via `docker-compose run backend python -m backend.ml.train_all`)
> so the API can load the models.

---

## Local Development (no Docker)

```bash
# Python env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Generate synthetic dataset (100k+ rows) -> data/pump_telemetry.csv + SQLite
python -m data.data_generator

# 2) Train all 3 models (logs to MLflow, writes ./models)
python -m backend.ml.train_all

# 3) Run the API
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 4) Frontend
cd frontend
npm install
npm run dev          # http://localhost:5173
```

**Recommended run order:** `generate data → train → launch API → launch UI`.

---

## ML Pipeline & Models

| # | Model | Task | Algorithm | Key metrics |
|---|-------|------|-----------|-------------|
| 1 | Failure classifier | P(failure within 7 days) | XGBoost | ROC AUC, Precision, Recall, F1 (+ SHAP) |
| 2 | RUL regressor | Remaining Useful Life (days) | XGBoost Regressor | RMSE, MAE, R² |
| 3 | Degradation forecaster | Health trend from sequences | PyTorch LSTM | RMSE / MAE on horizon |

Pipeline stages: **preprocessing → feature engineering → split → train → evaluate → MLflow logging → registry → inference API**.

---

## MLflow

```bash
# Launch the MLflow UI (local)
mlflow ui --backend-store-uri ./mlflow/mlruns --port 5000
# -> http://localhost:5000
```
Each training run logs parameters, metrics, and artifacts (plots, SHAP, model files)
and registers the model under the `oil_gas_pump_prediction` experiment.

---

## API Documentation

Interactive Swagger UI: **http://localhost:8000/docs**

| Method | Endpoint              | Description |
|--------|-----------------------|-------------|
| GET    | `/health`             | Liveness + model load status |
| POST   | `/predict/failure`    | Failure probability for a sensor reading |
| POST   | `/predict/rul`        | Remaining Useful Life (days) |
| POST   | `/predict/anomaly`    | Anomaly risk score + early-warning level |
| GET    | `/dashboard/summary`  | Fleet KPIs (totals, alerts, avg health, RUL) |
| GET    | `/pump/{id}`          | Per-pump telemetry trends + latest predictions |

---

## Dashboard
- **Overview** — animated KPI cards, fleet trend charts, risk heatmap.
- **Pump Detail** — pressure/vibration/temperature/RPM trends, health gauge, anomaly timeline, failure prob + RUL.
- **AI Insights** — SHAP explainability, top failure drivers, feature importance, prediction confidence.
- **Alert Management** — warning/critical tables and maintenance recommendations.

Theme: dark, futuristic industrial IoT (Tesla / SCADA inspired).

---

## Extra Features
- `backend/ml/drift_sim.py` — inject drift into telemetry to simulate model degradation.
- `backend/ml/retrain.py` — retrain pipeline on latest data.
- `backend/ml/batch_predict.py` — score the whole dataset, export predictions CSV.
- `/pump/{id}` PDF maintenance report via `reportlab` (`backend/app/services/report.py`).

---

## Screenshots
Place exported PNGs in `screenshots/`:
- `screenshots/overview.png`
- `screenshots/pump_detail.png`
- `screenshots/ai_insights.png`
- `screenshots/alerts.png`

---

## Future Improvements
- Replace synthetic generator with a real historian / OPC-UA connector.
- Add authentication (OAuth2 / JWT) and role-based access.
- Model monitoring dashboard with live drift metrics.
- Multi-horizon survival analysis for RUL.
- Kubernetes manifests + CI/CD pipeline.
