"""In-memory async event broadcaster for real-time Server-Sent Events (SSE)."""

import asyncio
import json
from typing import AsyncGenerator, Set
from app.core.logging import logger


class EventBroadcaster:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        logger.info(f"SSE client connected. Active subscribers: {len(self._subscribers)}")
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)
        logger.info(f"SSE client disconnected. Remaining subscribers: {len(self._subscribers)}")

    async def publish(self, event: str, data: dict) -> int:
        """Publish an event to all connected SSE clients."""
        payload = {
            "event": event,
            "data": json.dumps(data),
        }
        dead_queues = set()
        count = 0
        for q in self._subscribers:
            try:
                q.put_nowait(payload)
                count += 1
            except asyncio.QueueFull:
                dead_queues.add(q)

        for dq in dead_queues:
            self._subscribers.discard(dq)

        return count

    async def event_generator(self, queue: asyncio.Queue) -> AsyncGenerator[dict, None]:
        try:
            # Yield an initial heartbeat / connection event
            yield {
                "event": "connected",
                "data": json.dumps({"status": "streaming", "message": "ClimateShield Real-Time Telemetry Stream Connected"}),
            }
            while True:
                # Wait for next event or heartbeat every 15s
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield msg
                except asyncio.TimeoutError:
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"type": "ping"}),
                    }
        except asyncio.CancelledError:
            pass
        finally:
            self.unsubscribe(queue)


broadcaster = EventBroadcaster()
