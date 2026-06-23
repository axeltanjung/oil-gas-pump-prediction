"""
FastAPI application entrypoint.

Run:
    uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import dashboard, health, insights, predict, pump
from .core.config import settings
from .core.logging_config import get_logger

log = get_logger("api")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "Predictive maintenance API for Oil & Gas pumps: failure probability, "
        "Remaining Useful Life (RUL), and anomaly / early-warning scoring."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    log.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---- Routers ----
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(pump.router)
app.include_router(insights.router)


@app.get("/", tags=["root"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/predict/failure",
            "/predict/rul",
            "/predict/anomaly",
            "/dashboard/summary",
            "/dashboard/alerts",
            "/dashboard/risk-heatmap",
            "/pump/{id}",
            "/pump/{id}/report",
            "/insights/drivers",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
