"""
T101 [US2]: Dapr binding endpoints for scheduled jobs

Handles Dapr input bindings:
- reminder-cron: Triggered every 5 minutes to process due reminders

These endpoints are called by Dapr runtime, not by users directly.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from services.kafka_service import KafkaService
from services.reminder_scheduler import ReminderScheduler
from deps import get_kafka_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dapr", tags=["dapr-bindings"])


@router.post("/reminders/cron")
async def reminder_cron_trigger(
    session: AsyncSession = Depends(get_async_session),
    kafka_service: KafkaService = Depends(get_kafka_service)
):
    """
    T101: Dapr Cron binding endpoint for reminder scheduler.

    Called by Dapr every 5 minutes via reminder-cron binding.

    Workflow:
    1. Create ReminderScheduler instance
    2. Run scheduler (find due reminders, publish events)
    3. Return summary

    Returns:
        dict: Processing summary (reminders_found, reminders_sent, status)
    """
    logger.info("[Dapr Cron] reminder_cron_trigger called")

    try:
        # Create scheduler
        scheduler = ReminderScheduler(
            db_session=session,
            kafka_service=kafka_service
        )

        # Run scheduler
        result = await scheduler.run()

        logger.info(
            f"[Dapr Cron] Reminder scheduler completed: {result}"
        )

        return result

    except Exception as e:
        logger.error(
            f"[Dapr Cron] Reminder scheduler failed: {str(e)}",
            exc_info=True
        )
        return {
            "status": "error",
            "error": str(e)
        }
