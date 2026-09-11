"""ClimateShield FastAPI Application."""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api.router import api_router
from app.api.v1.system import router as root_system_router

import asyncio
import math
import random
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from app.models import Base
from app.core.database import engine, SessionLocal
from app.schemas.telemetry import TelemetryPayload
from app.services.telemetry_service import TelemetryService


async def live_telemetry_loop():
    """Background simulator generating continuous real-time IoT and river telemetry ticks."""
    logger.info("[LIVE_TELEMETRY] Real-time IoT background streamer initialized.")
    base_levels = {"RN-01": 2.45, "RN-02": 2.10, "RN-03": 1.75}
    step = 0
    while True:
        try:
            await asyncio.sleep(4.0)
            step += 1
            db = SessionLocal()
            try:
                service = TelemetryService(db)
                # Alternate between river nodes
                node_code = "RN-01" if (step % 2 == 0) else "RN-02"
                oscillation = round(math.sin(step * 0.2) * 0.16, 2)
                wl = round(base_levels[node_code] + oscillation + random.uniform(0.01, 0.03), 2)
                rf = round(max(0.0, 5.0 + math.cos(step * 0.1) * 3.5), 1)

                payload = TelemetryPayload(
                    message_id=str(uuid.uuid4()),
                    node_code=node_code,
                    timestamp=datetime.now(timezone.utc),
                    water_level_m=wl,
                    rainfall_mm=rf,
                    temperature_c=round(28.2 + math.sin(step * 0.05) * 0.8, 1),
                    battery_percent=random.choice([92, 93, 94]),
                    signal_percent=random.choice([96, 97, 98]),
                    is_simulated=True,
                )
                service.process_telemetry(payload)
            finally:
                db.close()
        except asyncio.CancelledError:
            logger.info("[LIVE_TELEMETRY] Real-time streamer stopped cleanly.")
            break
        except Exception as e:
            logger.debug(f"[LIVE_TELEMETRY] Background telemetry tick error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables if not present
    Base.metadata.create_all(bind=engine)
    # Start live real-time telemetry background task
    telemetry_task = asyncio.create_task(live_telemetry_loop())
    try:
        yield
    finally:
        telemetry_task.cancel()
        try:
            await telemetry_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ClimateShield Operational Intelligence and Resilience Command API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# Request ID and Structured Logging Middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response.headers["X-Request-ID"] = request_id

    extra = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
        extra=extra,
    )
    return response


# Register Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include Routers
app.include_router(root_system_router)  # Provides GET /health at root
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "ClimateShield API",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }
