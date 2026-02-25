"""
T133: NotificationRepository - Log notification delivery status to database
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config import get_settings

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repository for logging notification delivery status."""

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

    async def log_sent(
        self,
        user_id: str,
        task_id: str,
        channel: str,
        message: str,
        sent_at: datetime,
    ) -> int:
        """
        Log successfully sent notification.

        Args:
            user_id: User UUID
            task_id: Task UUID
            channel: Notification channel (email/push)
            message: Notification message content
            sent_at: Timestamp when notification was sent

        Returns:
            Database ID of the logged notification
        """
        engine = await self._get_engine()

        query = text("""
            INSERT INTO notifications (user_id, task_id, type, message, sent_at, delivery_status, created_at)
            VALUES (:user_id, :task_id, :type, :message, :sent_at, 'sent', NOW())
            RETURNING id
        """)

        async with engine.begin() as conn:
            result = await conn.execute(
                query,
                {
                    "user_id": user_id,
                    "task_id": task_id,
                    "type": channel,
                    "message": message,
                    "sent_at": sent_at,
                },
            )
            notification_id = result.scalar_one()
            logger.info(f"Logged sent notification: {notification_id}")
            return notification_id

    async def log_failed(
        self,
        user_id: str,
        task_id: str,
        channel: str,
        message: str,
        error_message: str,
        failed_at: datetime,
    ) -> int:
        """
        Log failed notification attempt.

        Args:
            user_id: User UUID
            task_id: Task UUID
            channel: Notification channel (email/push)
            message: Notification message content
            error_message: Error details
            failed_at: Timestamp when notification failed

        Returns:
            Database ID of the logged notification
        """
        engine = await self._get_engine()

        query = text("""
            INSERT INTO notifications (user_id, task_id, type, message, sent_at, delivery_status, error_message, created_at)
            VALUES (:user_id, :task_id, :type, :message, :failed_at, 'failed', :error_message, NOW())
            RETURNING id
        """)

        async with engine.begin() as conn:
            result = await conn.execute(
                query,
                {
                    "user_id": user_id,
                    "task_id": task_id,
                    "type": channel,
                    "message": message,
                    "failed_at": failed_at,
                    "error_message": error_message,
                },
            )
            notification_id = result.scalar_one()
            logger.error(f"Logged failed notification: {notification_id} - {error_message}")
            return notification_id

    async def close(self):
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
