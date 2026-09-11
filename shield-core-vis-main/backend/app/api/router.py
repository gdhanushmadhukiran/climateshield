"""Central API v1 router."""

from fastapi import APIRouter
from app.api.v1 import (
    city,
    risk,
    assets,
    incidents,
    alerts,
    optimization,
    river,
    data_sources,
    forecast,
    cascade,
    system,
    telemetry,
    stream,
    sensors,
    ml,
    simulation,
    agentic,
)

api_router = APIRouter()

api_router.include_router(city.router)
api_router.include_router(risk.router)
api_router.include_router(assets.router)
api_router.include_router(incidents.router)
api_router.include_router(alerts.router)
api_router.include_router(optimization.router)
api_router.include_router(river.router)
api_router.include_router(data_sources.router)
api_router.include_router(forecast.router)
api_router.include_router(cascade.router)
api_router.include_router(system.router)
api_router.include_router(telemetry.router)
api_router.include_router(stream.router)
api_router.include_router(sensors.router)
api_router.include_router(ml.router)
api_router.include_router(simulation.router)
api_router.include_router(agentic.router)


