# Application settings (pydantic-settings), sourced from environment .env.
# Co-authored with CoCo

from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Oil & Gas Pump Failure Prediction API"
    version: str = "1.0.0"

    data_dir: str = os.path.join(ROOT, "data")
    model_dir: str = os.path.join(ROOT, "models")
    sqlite_path: str = os.path.join(ROOT, "data", "pumps.db")
    exports_dir: str = os.path.join(ROOT, "exports")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Alert thresholds
    failure_prob_warning: float = 0.40
    failure_prob_critical: float = 0.70
    rul_warning_days: float = 14
    rul_critical_days: float = 5
    anomaly_warning: float = 0.50
    anomaly_critical: float = 0.75

    cors_origins: list[str] = []


settings = Settings()
