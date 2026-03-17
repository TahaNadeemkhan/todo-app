"""
T037-T041: KafkaService - Event Publishing Service using Dapr HTTP API
Bypasses the buggy Dapr Python SDK to ensure stability.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from uuid import uuid4
import httpx
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class BufferedEvent(BaseModel):
    """Event stored in buffer when Kafka is unavailable."""
    event_id: str
    topic: str
    event_type: str
    data: Dict[str, Any]
    retry_count: int = 0
    buffered_at: datetime


class KafkaService:
    """
    T037: Kafka event publishing service using Dapr HTTP API.
    """

    def __init__(
        self,
        dapr_http_port: str = "3500",
        max_retries: int = 3,
        enable_buffer: bool = False,
        max_buffer_size: int = 1000,
        pubsub_name: str = "pubsub-kafka"
    ):
        self.dapr_url = f"http://localhost:{dapr_http_port}/v1.0/publish/{pubsub_name}"
        self.max_retries = max_retries
        self.enable_buffer = enable_buffer
        self.max_buffer_size = max_buffer_size

        # In-memory buffer
        self._buffer: List[BufferedEvent] = []
        self._buffer_lock = asyncio.Lock()

        logger.info(f"KafkaService (HTTP) initialized at {self.dapr_url}")

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        event_id: Optional[str] = None,
        use_buffer_on_failure: bool = False
    ) -> str:
        if event_id is None:
            event_id = str(uuid4())

        event = {
            "event_id": event_id,
            "event_type": event_type,
            "schema_version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "data": data
        }

        url = f"{self.dapr_url}/{topic}"
        
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=event, timeout=5.0)
                    response.raise_for_status()
                    logger.info(f"Event {event_id} published to {topic}")
                    return event_id
            except Exception as e:
                last_exception = e
                logger.warning(f"Publish failed (attempt {attempt+1}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)

        if self.enable_buffer and use_buffer_on_failure:
            await self._buffer_event(event_id, topic, event_type, data)
            return event_id

        raise last_exception

    async def _buffer_event(self, event_id, topic, event_type, data):
        async with self._buffer_lock:
            if len(self._buffer) < self.max_buffer_size:
                self._buffer.append(BufferedEvent(
                    event_id=event_id, topic=topic, event_type=event_type,
                    data=data, buffered_at=datetime.now(timezone.utc)
                ))

    def close(self):
        pass


def create_kafka_service(enable_buffer: bool = False, max_retries: int = 3) -> KafkaService:
    import os
    port = os.getenv("DAPR_HTTP_PORT", "3500")
    return KafkaService(dapr_http_port=port, enable_buffer=enable_buffer, max_retries=max_retries)
