"""
T117: EventLogRepository - Track processed event_ids for idempotency

Ensures duplicate events are not processed twice (network retries, Kafka redelivery).
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base


logger = logging.getLogger(__name__)


# SQLAlchemy Base
Base = declarative_base()


class EventLog(Base):
    """
    Event log table for idempotency tracking.

    Stores processed event_ids to prevent duplicate processing.
    """

    __tablename__ = "event_logs"

    event_id = Column(String(255), primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=False)


class EventLogRepository:
    """
    T117: Repository for event log operations.

    Provides idempotency guarantees by tracking processed events.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize EventLogRepository.

        Args:
            db_session: SQLAlchemy async session
        """
        self.session = db_session

    async def has_processed(self, event_id: str) -> bool:
        """
        Check if event has already been processed.

        Args:
            event_id: Event UUID to check

        Returns:
            bool: True if event was already processed, False otherwise
        """
        stmt = select(EventLog).where(EventLog.event_id == event_id)
        result = await self.session.execute(stmt)
        event_log = result.scalar_one_or_none()

        if event_log:
            logger.debug(
                f"Event already processed: event_id={event_id}, "
                f"processed_at={event_log.processed_at}"
            )
            return True

        return False

    async def mark_as_processed(
        self,
        event_id: str,
        event_type: str,
        processed_at: datetime
    ) -> EventLog:
        """
        Mark event as processed for idempotency.

        Args:
            event_id: Event UUID
            event_type: Event type (e.g., "task.completed.v1")
            processed_at: Timestamp when event was processed

        Returns:
            EventLog: Created event log record

        Raises:
            Exception: If database operation fails
        """
        event_log = EventLog(
            event_id=event_id,
            event_type=event_type,
            processed_at=processed_at
        )

        self.session.add(event_log)
        await self.session.commit()
        await self.session.refresh(event_log)

        logger.info(
            f"Event marked as processed: event_id={event_id}, "
            f"event_type={event_type}"
        )

        return event_log

    async def get_event_log(self, event_id: str) -> Optional[EventLog]:
        """
        Get event log record by event_id.

        Args:
            event_id: Event UUID

        Returns:
            Optional[EventLog]: Event log record or None if not found
        """
        stmt = select(EventLog).where(EventLog.event_id == event_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


# ============================================================================
# Factory Function
# ============================================================================

def create_event_log_repository(db_session: AsyncSession) -> EventLogRepository:
    """
    Factory function to create EventLogRepository instance.

    Args:
        db_session: SQLAlchemy async session

    Returns:
        EventLogRepository: Configured instance
    """
    return EventLogRepository(db_session)
