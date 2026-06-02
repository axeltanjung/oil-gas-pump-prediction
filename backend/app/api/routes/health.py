"""
Health / liveness endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter

from ...core.config import settings
from ...core.db import table_exists
from ...schemas.io import HealthResponse
from ...services import inference

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.version,
        models_loaded=inference.store.status(),
        database_ready=table_exists("telemetry"),
    )
