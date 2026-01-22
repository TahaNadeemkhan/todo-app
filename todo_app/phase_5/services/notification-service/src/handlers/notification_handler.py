"""
T134-T135: NotificationHandler - Orchestrate email/push sending with retry logic
"""

import logging
import asyncio
import uuid
from datetime import datetime
from typing import Optional
import httpx

from schemas import ReminderDueEvent, NotificationChannelEnum, NotificationSentData, NotificationFailedData
from config import get_settings
from .email_handler import EmailHandler
from .push_handler import PushHandler
from repositories import NotificationRepository, EventLogRepository

logger = logging.getLogger(__name__)


class NotificationHandler:
    """
    Orchestrator for sending notifications via multiple channels with retry logic.
    """

    def __init__(self):
        self.settings = get_settings()
        self.email_handler = EmailHandler()
        self.push_handler = PushHandler()
        self.notification_repo = NotificationRepository()
        self.event_log_repo = EventLogRepository()

    async def handle_reminder_due(self, event: ReminderDueEvent) -> None:
        """
        Handle reminder.due event - main entry point from Dapr Pub/Sub consumer.

        This method:
        1. Checks idempotency (skip if already processed)
        2. Sends notifications via requested channels (email/push)
        3. Implements retry logic with exponential backoff
        4. Publishes notification.sent or notification.failed events back to Kafka
        5. Logs delivery status to database

        Args:
            event: ReminderDueEvent from Kafka
        """
        event_id = event.event_id
        data = event.data

        logger.info(f"Handling reminder.due event {event_id} for task {data.task_id}")

        # Idempotency check
        if await self.event_log_repo.is_event_processed(event_id, "notification-service"):
            logger.warning(f"Event {event_id} already processed, skipping")
            return

        # Parse due_at datetime
        try:
            due_at = datetime.fromisoformat(data.due_at.replace("Z", "+00:00"))
        except Exception as e:
            logger.error(f"Failed to parse due_at: {e}")
            return

        # Send notifications via each requested channel
        for channel in data.channels:
            success = False
            error_message = None

            # Retry logic
            for attempt in range(1, self.settings.max_retry_attempts + 1):
                try:
                    if channel == NotificationChannelEnum.EMAIL:
                        success = await self._send_email_with_retry(
                            data.user_email,
                            data.task_title,
                            data.task_description,
                            due_at,
                            data.remind_before,
                            attempt,
                        )
                    elif channel == NotificationChannelEnum.PUSH:
                        # TODO: Retrieve user's FCM token from database
                        fcm_token = None  # Placeholder
                        success = await self._send_push_with_retry(
                            data.user_id,
                            data.task_title,
                            data.task_description,
                            due_at,
                            data.remind_before,
                            fcm_token,
                            attempt,
                        )

                    if success:
                        logger.info(f"Notification sent successfully via {channel} on attempt {attempt}")
                        break  # Success - exit retry loop

                except Exception as e:
                    error_message = str(e)
                    logger.error(f"Attempt {attempt} failed for {channel}: {e}")

                    if attempt < self.settings.max_retry_attempts:
                        # Exponential backoff
                        backoff_seconds = min(
                            self.settings.retry_backoff_base ** attempt,
                            self.settings.retry_backoff_max,
                        )
                        logger.info(f"Retrying in {backoff_seconds} seconds...")
                        await asyncio.sleep(backoff_seconds)

            # Log delivery status and publish result event
            message = f"Reminder: {data.task_title} is due on {due_at.strftime('%B %d, %Y at %I:%M %p')}"

            if success:
                await self._log_and_publish_sent(
                    data.user_id,
                    data.task_id,
                    channel.value,
                    message,
                )
            else:
                await self._log_and_publish_failed(
                    data.user_id,
                    data.task_id,
                    channel.value,
                    message,
                    error_message or "Unknown error after max retries",
                )

        # Mark event as processed
        await self.event_log_repo.mark_event_processed(
            event_id, event.event_type, "notification-service"
        )

    async def _send_email_with_retry(
        self,
        to_email: str,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
        remind_before: str,
        attempt: int,
    ) -> bool:
        """Send email with attempt logging."""
        logger.info(f"Sending email (attempt {attempt}): {to_email}")
        return await self.email_handler.send_reminder_email(
            to_email, task_title, task_description, due_at, remind_before
        )

    async def _send_push_with_retry(
        self,
        user_id: str,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
        remind_before: str,
        fcm_token: Optional[str],
        attempt: int,
    ) -> bool:
        """Send push notification with attempt logging."""
        logger.info(f"Sending push (attempt {attempt}): {user_id}")
        return await self.push_handler.send_reminder_push(
            user_id, task_title, task_description, due_at, remind_before, fcm_token
        )

    async def _log_and_publish_sent(
        self,
        user_id: str,
        task_id: str,
        channel: str,
        message: str,
    ) -> None:
        """Log sent notification and publish notification.sent event to Kafka."""
        sent_at = datetime.utcnow()

        # Log to database
        notification_id = await self.notification_repo.log_sent(
            user_id, task_id, channel, message, sent_at
        )

        # Publish notification.sent event via Dapr Pub/Sub
        await self._publish_notification_event(
            event_type="notification.sent.v1",
            data=NotificationSentData(
                notification_id=notification_id,
                user_id=user_id,
                task_id=task_id,
                channel=channel,  # type: ignore
                message=message,
                sent_at=sent_at.isoformat() + "Z",
            ),
        )

    async def _log_and_publish_failed(
        self,
        user_id: str,
        task_id: str,
        channel: str,
        message: str,
        error: str,
    ) -> None:
        """Log failed notification and publish notification.failed event to Kafka."""
        failed_at = datetime.utcnow()

        # Log to database
        notification_id = await self.notification_repo.log_failed(
            user_id, task_id, channel, message, error, failed_at
        )

        # Publish notification.failed event via Dapr Pub/Sub
        await self._publish_notification_event(
            event_type="notification.failed.v1",
            data=NotificationFailedData(
                notification_id=notification_id,
                user_id=user_id,
                task_id=task_id,
                channel=channel,  # type: ignore
                message=message,
                error=error,
                failed_at=failed_at.isoformat() + "Z",
            ),
        )

    async def _publish_notification_event(self, event_type: str, data) -> None:
        """Publish notification event to Kafka via Dapr Pub/Sub API."""
        event_payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "schema_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data.model_dump(),
        }

        dapr_url = f"http://localhost:{self.settings.dapr_http_port}/v1.0/publish/{self.settings.dapr_pubsub_name}/{self.settings.dapr_notifications_topic}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(dapr_url, json=event_payload, timeout=5.0)
                response.raise_for_status()
                logger.info(f"Published {event_type} event to Kafka")
        except Exception as e:
            logger.error(f"Failed to publish {event_type} event: {e}")

    async def close(self):
        """Cleanup resources."""
        await self.notification_repo.close()
        await self.event_log_repo.close()
