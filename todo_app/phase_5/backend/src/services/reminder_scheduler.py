"""
T098-T100 [P] [US2]: ReminderScheduler - Service for finding and sending due reminders

Scheduled service that:
1. Finds tasks with unsent reminders that are due
2. Publishes reminder.due.v1 events to Kafka
3. Marks reminders as sent

Triggered by Dapr Cron binding every 5 minutes.

Part of TDD Green Phase - implements the reminder scheduling logic.
"""

import logging
from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task
from models.task_reminder import TaskReminder
from repositories.reminder_repository import ReminderRepository
from services.kafka_service import KafkaService


logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    T098-T100: Scheduler service for processing due reminders.

    Responsibilities:
    - Find unsent reminders that are due (T099)
    - Publish reminder.due events to Kafka (T100)
    - Mark reminders as sent after successful publishing
    - Handle errors gracefully (log but don't crash)
    """

    def __init__(
        self,
        db_session: AsyncSession,
        kafka_service: KafkaService
    ):
        """
        Initialize ReminderScheduler.

        Args:
            db_session: SQLAlchemy async session
            kafka_service: Kafka event publishing service
        """
        self.repository = ReminderRepository(db_session)
        self.kafka = kafka_service
        self.session = db_session

    async def run(self) -> dict:
        """
        Main entry point for the reminder scheduler.

        Called by Dapr Cron binding every 5 minutes.

        Returns:
            dict: Summary of processing results
        """
        logger.info("ReminderScheduler starting...")

        try:
            # Step 1: Find due reminders
            due_reminders = await self.find_due_reminders()

            if not due_reminders:
                logger.info("No due reminders found")
                return {
                    "status": "success",
                    "reminders_found": 0,
                    "reminders_sent": 0
                }

            logger.info(f"Found {len(due_reminders)} due reminders")

            # Step 2: Publish events
            sent_count = await self.publish_reminder_events(due_reminders)

            logger.info(
                f"ReminderScheduler completed: {sent_count}/{len(due_reminders)} sent"
            )

            return {
                "status": "success",
                "reminders_found": len(due_reminders),
                "reminders_sent": sent_count
            }

        except Exception as e:
            logger.error(f"ReminderScheduler error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    async def find_due_reminders(
        self,
        current_time: datetime | None = None
    ) -> List[Tuple[Task, TaskReminder]]:
        """
        T099: Find all reminders that are due to be sent.

        Queries for:
        - Tasks with due_at set
        - Tasks not completed
        - Reminders not sent yet (sent_at IS NULL)
        - Reminder time has arrived (due_at - remind_before <= current_time)

        Args:
            current_time: Current time (defaults to now)

        Returns:
            List[Tuple[Task, TaskReminder]]: List of (Task, TaskReminder) tuples
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Delegate to repository
        due_reminders = await self.repository.find_unsent_reminders(current_time)

        logger.info(
            f"find_due_reminders: Found {len(due_reminders)} reminders at {current_time}"
        )

        return due_reminders

    async def publish_reminder_events(
        self,
        due_reminders: List[Tuple[Task, TaskReminder]]
    ) -> int:
        """
        T100: Publish reminder.due.v1 events to Kafka for each due reminder.

        For each reminder:
        1. Build event payload
        2. Publish to 'reminders' topic
        3. Mark reminder as sent
        4. Handle errors gracefully (log but continue processing)

        Args:
            due_reminders: List of (Task, TaskReminder) tuples

        Returns:
            int: Number of reminders successfully sent
        """
        sent_count = 0

        for task, reminder in due_reminders:
            try:
                # Build event payload
                event_data = {
                    "reminder_id": reminder.id,
                    "task_id": task.id,
                    "user_id": task.user_id,
                    "task_title": task.title,
                    "due_at": task.due_at.isoformat().replace("+00:00", "Z"),
                    "remind_before": reminder.remind_before,
                    "channels": reminder.channels,
                }

                # Publish event
                await self.kafka.publish_event(
                    topic="reminders",
                    event_type="reminder.due.v1",
                    data=event_data
                )

                logger.info(
                    f"reminder.due event published: reminder_id={reminder.id}, "
                    f"task_id={task.id}"
                )

                # Mark as sent
                reminder.sent_at = datetime.now(timezone.utc)
                await self.session.commit()

                sent_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to publish reminder.due event: reminder_id={reminder.id}, "
                    f"error={str(e)}"
                )
                # Continue processing other reminders
                continue

        return sent_count


# ============================================================================
# Factory Function
# ============================================================================

def create_reminder_scheduler(
    db_session: AsyncSession,
    kafka_service: KafkaService
) -> ReminderScheduler:
    """
    Factory function to create ReminderScheduler instance.

    Args:
        db_session: SQLAlchemy async session
        kafka_service: Kafka event publishing service

    Returns:
        ReminderScheduler: Configured instance
    """
    return ReminderScheduler(db_session=db_session, kafka_service=kafka_service)
