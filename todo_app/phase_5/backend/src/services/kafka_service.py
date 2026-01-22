"""
T037-T041: KafkaService - Event Publishing Service with Dapr Pub/Sub

Responsibilities:
- T037: Implement KafkaService class
- T038: publish_event method with event serialization and error handling
- T039: Generate unique event_id (UUID) for idempotency
- T040: Retry logic with exponential backoff for Kafka failures
- T041: In-memory buffer for events when Kafka is unavailable (max 1000 events)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from uuid import uuid4

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError
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
    T037: Kafka event publishing service using Dapr Pub/Sub.

    Features:
    - UUID-based event_id generation for idempotency (T039)
    - Retry logic with exponential backoff (T040)
    - In-memory event buffer for Kafka downtime (T041)
    - JSON event serialization (T038)
    """

    def __init__(
        self,
        dapr_client: Optional[DaprClient] = None,
        bootstrap_servers: Optional[str] = None,
        max_retries: int = 3,
        enable_buffer: bool = False,
        max_buffer_size: int = 1000,
        pubsub_name: str = "kafka-pubsub"
    ):
        """
        Initialize KafkaService.

        Args:
            dapr_client: Dapr client for pub/sub (if None, creates new one)
            bootstrap_servers: Kafka bootstrap servers (for testcontainers)
            max_retries: Maximum retry attempts for failed publishes (default: 3)
            enable_buffer: Enable in-memory buffer for Kafka downtime (default: False)
            max_buffer_size: Maximum events in buffer (default: 1000)
            pubsub_name: Dapr pub/sub component name (default: kafka-pubsub)
        """
        self.dapr_client = dapr_client or DaprClient()
        self.bootstrap_servers = bootstrap_servers
        self.max_retries = max_retries
        self.enable_buffer = enable_buffer
        self.max_buffer_size = max_buffer_size
        self.pubsub_name = pubsub_name

        # T041: In-memory buffer for events when Kafka is unavailable
        self._buffer: List[BufferedEvent] = []
        self._buffer_lock = asyncio.Lock()

        logger.info(
            f"KafkaService initialized: max_retries={max_retries}, "
            f"buffer_enabled={enable_buffer}, max_buffer_size={max_buffer_size}"
        )

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        event_id: Optional[str] = None,
        use_buffer_on_failure: bool = False
    ) -> str:
        """
        T038: Publish event to Kafka topic via Dapr Pub/Sub.

        Args:
            topic: Kafka topic name (e.g., "task-events", "reminders", "notifications")
            event_type: Event type with version (e.g., "task.created.v1")
            data: Event data payload (dict)
            event_id: Optional event ID (generates UUID if not provided)
            use_buffer_on_failure: Buffer event if Kafka is unavailable (default: False)

        Returns:
            str: Generated or provided event_id

        Raises:
            Exception: If publish fails after max retries and buffer is disabled
        """
        # T039: Generate unique event_id (UUID) for idempotency
        if event_id is None:
            event_id = str(uuid4())

        # Build event envelope
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "schema_version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "data": data
        }

        # T040: Attempt to publish with retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                await self._publish_to_dapr(topic, event)
                logger.info(
                    f"Event published successfully: event_id={event_id}, "
                    f"event_type={event_type}, topic={topic}, attempt={attempt + 1}"
                )
                return event_id

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Failed to publish event (attempt {attempt + 1}/{self.max_retries + 1}): "
                    f"event_id={event_id}, error={str(e)}"
                )

                # If not last attempt, wait with exponential backoff
                if attempt < self.max_retries:
                    backoff_seconds = 2 ** attempt  # 1s, 2s, 4s, 8s
                    logger.info(f"Retrying in {backoff_seconds}s...")
                    await asyncio.sleep(backoff_seconds)

        # All retries failed
        logger.error(
            f"Event publish failed after {self.max_retries + 1} attempts: "
            f"event_id={event_id}, event_type={event_type}"
        )

        # T041: Buffer event if enabled and requested
        if self.enable_buffer and use_buffer_on_failure:
            await self._buffer_event(
                event_id=event_id,
                topic=topic,
                event_type=event_type,
                data=data
            )
            logger.info(f"Event buffered: event_id={event_id}, buffer_size={len(self._buffer)}")
            return event_id

        # No buffer or buffer disabled, raise exception
        raise last_exception

    async def _publish_to_dapr(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Internal: Publish event to Dapr Pub/Sub.

        Args:
            topic: Kafka topic name
            event: Event envelope (dict)

        Raises:
            Exception: If Dapr publish fails
        """
        try:
            # Use Dapr Pub/Sub to publish event
            await self.dapr_client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=event,
                data_content_type="application/json"
            )
        except DaprInternalError as e:
            # Re-raise with more context
            raise Exception(f"Dapr Pub/Sub error: {str(e)}") from e
        except Exception as e:
            # Re-raise all other exceptions
            raise Exception(f"Failed to publish event: {str(e)}") from e

    async def _buffer_event(
        self,
        event_id: str,
        topic: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """
        T041: Buffer event in-memory when Kafka is unavailable.

        Args:
            event_id: Event UUID
            topic: Kafka topic name
            event_type: Event type
            data: Event data payload

        Raises:
            Exception: If buffer is full (exceeds max_buffer_size)
        """
        async with self._buffer_lock:
            # Check buffer size limit
            if len(self._buffer) >= self.max_buffer_size:
                raise Exception(
                    f"Buffer full: max_buffer_size={self.max_buffer_size} reached. "
                    "Cannot buffer more events."
                )

            # Add to buffer
            buffered_event = BufferedEvent(
                event_id=event_id,
                topic=topic,
                event_type=event_type,
                data=data,
                retry_count=0,
                buffered_at=datetime.now(timezone.utc)
            )
            self._buffer.append(buffered_event)

            logger.info(
                f"Event added to buffer: event_id={event_id}, "
                f"buffer_size={len(self._buffer)}/{self.max_buffer_size}"
            )

    def get_buffer_size(self) -> int:
        """
        Get current buffer size (for monitoring/testing).

        Returns:
            int: Number of events in buffer
        """
        return len(self._buffer)

    async def flush_buffer(self) -> Dict[str, int]:
        """
        Attempt to republish all buffered events.

        Returns:
            Dict[str, int]: {"published": count, "failed": count}
        """
        if not self._buffer:
            return {"published": 0, "failed": 0}

        logger.info(f"Flushing buffer: {len(self._buffer)} events")

        published_count = 0
        failed_count = 0

        async with self._buffer_lock:
            remaining_events = []

            for buffered_event in self._buffer:
                try:
                    # Build event envelope
                    event = {
                        "event_id": buffered_event.event_id,
                        "event_type": buffered_event.event_type,
                        "schema_version": "1.0",
                        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        "data": buffered_event.data
                    }

                    # Attempt to publish
                    await self._publish_to_dapr(buffered_event.topic, event)
                    published_count += 1
                    logger.info(f"Buffered event published: event_id={buffered_event.event_id}")

                except Exception as e:
                    # Increment retry count and keep in buffer
                    buffered_event.retry_count += 1
                    remaining_events.append(buffered_event)
                    failed_count += 1
                    logger.warning(
                        f"Failed to publish buffered event: event_id={buffered_event.event_id}, "
                        f"retry_count={buffered_event.retry_count}, error={str(e)}"
                    )

            # Update buffer with remaining events
            self._buffer = remaining_events

        logger.info(
            f"Buffer flush complete: published={published_count}, "
            f"failed={failed_count}, remaining={len(self._buffer)}"
        )

        return {"published": published_count, "failed": failed_count}

    async def clear_buffer(self) -> int:
        """
        Clear all buffered events (for testing or manual intervention).

        Returns:
            int: Number of events cleared
        """
        async with self._buffer_lock:
            count = len(self._buffer)
            self._buffer.clear()
            logger.info(f"Buffer cleared: {count} events removed")
            return count

    def close(self) -> None:
        """
        Close Dapr client and cleanup resources.
        """
        if self.dapr_client:
            self.dapr_client.close()
            logger.info("KafkaService closed")


# ============================================================================
# Helper Functions
# ============================================================================

def create_kafka_service(
    enable_buffer: bool = False,
    max_retries: int = 3
) -> KafkaService:
    """
    Factory function to create KafkaService instance.

    Args:
        enable_buffer: Enable event buffering for Kafka downtime
        max_retries: Maximum retry attempts

    Returns:
        KafkaService: Configured instance
    """
    return KafkaService(
        max_retries=max_retries,
        enable_buffer=enable_buffer,
        max_buffer_size=1000
    )
