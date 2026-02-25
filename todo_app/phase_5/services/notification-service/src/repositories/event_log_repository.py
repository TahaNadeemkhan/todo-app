"""
Event Log Repository - Track processed events for idempotency
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from typing import Optional

from config import get_settings

logger = logging.getLogger(__name__)


class EventLogRepository:
    """Repository for tracking processed events to ensure idempotency."""

    def __init__(self):
        self.settings = get_settings()
        self._engine: Optional[AsyncEngine] = None

    async def _get_engine(self) -> AsyncEngine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self.settings.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
        return self._engine

    async def is_event_processed(self, event_id: str, consumer_service: str) -> bool:
        """
        Check if an event has already been processed by this consumer.

        Args:
            event_id: Unique event identifier
            consumer_service: Name of the consumer service (e.g., "notification-service")

        Returns:
            True if event already processed, False otherwise
        """
        engine = await self._get_engine()

        query = text("""
            SELECT COUNT(*) FROM event_log
            WHERE event_id = :event_id AND consumer_service = :consumer_service
        """)

        async with engine.begin() as conn:
            result = await conn.execute(
                query,
                {"event_id": event_id, "consumer_service": consumer_service},
            )
            count = result.scalar_one()
            return count > 0

    async def mark_event_processed(
        self,
        event_id: str,
        event_type: str,
        consumer_service: str,
        ttl_hours: int = 168,  # 7 days default
    ) -> None:
        """
        Mark an event as processed.

        Args:
            event_id: Unique event identifier
            event_type: Type of event (e.g., "reminder.due.v1")
            consumer_service: Name of the consumer service
            ttl_hours: Time-to-live in hours before this record can be cleaned up
        """
        engine = await self._get_engine()

        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        query = text("""
            INSERT INTO event_log (event_id, event_type, consumer_service, processed_at, expires_at)
            VALUES (:event_id, :event_type, :consumer_service, NOW(), :expires_at)
            ON CONFLICT (event_id, consumer_service) DO NOTHING
        """)

        async with engine.begin() as conn:
            await conn.execute(
                query,
                {
                    "event_id": event_id,
                    "event_type": event_type,
                    "consumer_service": consumer_service,
                    "expires_at": expires_at,
                },
            )
            logger.info(f"Marked event {event_id} as processed by {consumer_service}")

    async def cleanup_expired_events(self) -> int:
        """
        Remove expired event log entries (housekeeping).

        Returns:
            Number of deleted records
        """
        engine = await self._get_engine()

        query = text("""
            DELETE FROM event_log
            WHERE expires_at < NOW()
        """)

        async with engine.begin() as conn:
            result = await conn.execute(query)
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired event log entries")
            return deleted_count

    async def close(self):
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
