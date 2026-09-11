"""Server-Sent Events (SSE) real-time streaming endpoint."""

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.core.events import broadcaster

router = APIRouter(prefix="/stream", tags=["Real-Time Stream"])


@router.get(
    "/telemetry",
    summary="Real-time Server-Sent Events (SSE) telemetry stream for dashboard clients",
)
async def stream_telemetry(request: Request):
    queue = broadcaster.subscribe()
    return EventSourceResponse(broadcaster.event_generator(queue))
