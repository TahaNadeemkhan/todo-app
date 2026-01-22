"""
T118-T120: Dapr Pub/Sub consumer for task.completed events

Subscribes to task-events topic and triggers RecurrenceHandler for event processing.
"""

import logging
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class TaskCompletedConsumer:
    """
    T118-T120: Dapr Pub/Sub consumer for task.completed events.

    Responsibilities:
    - T118: Subscribe to task-events topic via Dapr Pub/Sub
    - T119: Filter for task.completed events
    - T120: Error handling and dead letter queue for failed events
    """

    def __init__(self, recurrence_handler):
        """
        Initialize TaskCompletedConsumer.

        Args:
            recurrence_handler: RecurrenceHandler instance for processing events
        """
        self.recurrence_handler = recurrence_handler

    def register_routes(self, app: FastAPI):
        """
        Register Dapr Pub/Sub routes with FastAPI app.

        Dapr requires specific endpoints:
        - GET /dapr/subscribe: Returns subscription configuration
        - POST /events: Event handler endpoint

        Args:
            app: FastAPI application instance
        """

        @app.get("/dapr/subscribe")
        async def subscribe():
            """
            T119: Dapr subscription endpoint.

            Returns subscription configuration for task-events topic
            with filter for task.completed events.

            Dapr calls this endpoint to discover subscriptions.
            """
            subscriptions = [
                {
                    "pubsubname": "task-pubsub",
                    "topic": "task-events",
                    "route": "/events",
                    "metadata": {
                        # T119: Filter for task.completed events only
                        "event.type": "task.completed.v1"
                    }
                }
            ]

            logger.info(
                "Dapr subscription endpoint called, "
                f"returning {len(subscriptions)} subscription(s)"
            )

            return subscriptions

        @app.post("/events")
        async def handle_event(request: Request):
            """
            T118: Event handler endpoint for task.completed events.

            Dapr publishes events to this endpoint after filtering.

            Expected payload (Dapr CloudEvent format):
            {
                "id": "event-uuid",
                "source": "backend-api",
                "type": "task.completed.v1",
                "datacontenttype": "application/json",
                "data": {
                    "task_id": "uuid",
                    "user_id": "uuid",
                    "completed_at": "2026-01-06T10:00:00Z",
                    "has_recurrence": true,
                    ...
                }
            }

            Returns:
                - 200: Event processed successfully
                - 400: Malformed event (will be sent to dead letter)
                - 500: Processing failed (Dapr will retry)
            """
            try:
                # Parse CloudEvent payload
                cloud_event = await request.json()

                logger.info(
                    f"Received event: type={cloud_event.get('type')}, "
                    f"id={cloud_event.get('id')}"
                )

                # Extract event data
                event_type = cloud_event.get("type")
                event_id = cloud_event.get("id")
                event_data = cloud_event.get("data", {})

                # T119: Verify event type (should be filtered by Dapr, but double-check)
                if event_type != "task.completed.v1":
                    logger.warning(
                        f"Unexpected event type received: {event_type}, "
                        f"expected task.completed.v1"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": "Invalid event type"}
                    )

                # Build internal event format for handler
                internal_event = {
                    "event_id": event_id,
                    "event_type": event_type,
                    "data": event_data
                }

                # T118: Process event via RecurrenceHandler
                await self.recurrence_handler.handle_task_completed(internal_event)

                logger.info(
                    f"Event processed successfully: event_id={event_id}"
                )

                # Return SUCCESS to Dapr (prevents retry)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"status": "success"}
                )

            except json.JSONDecodeError as e:
                # T120: Malformed JSON - send to dead letter queue (return 400)
                logger.error(
                    f"Malformed JSON in event payload: {str(e)}"
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Malformed JSON"}
                )

            except ValueError as e:
                # T120: Business logic error (validation, missing fields) - dead letter
                logger.error(
                    f"Validation error processing event: {str(e)}, "
                    f"event_id={cloud_event.get('id')}"
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": str(e)}
                )

            except Exception as e:
                # T120: Unexpected error - trigger Dapr retry (return 500)
                logger.exception(
                    f"Unexpected error processing event: {str(e)}, "
                    f"event_id={cloud_event.get('id')}"
                )
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": "Internal server error"}
                )


# ============================================================================
# Dead Letter Queue Configuration (T120)
# ============================================================================

"""
Dapr Dead Letter Queue Configuration:

In Dapr component YAML (components/task-pubsub.yaml), configure dead letter:

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
spec:
  type: pubsub.kafka
  metadata:
    - name: brokers
      value: "localhost:9092"
    - name: consumerGroup
      value: "recurring-task-service"
    - name: deadLetterTopic
      value: "task-events-dlq"

Events that return 4xx status codes will be sent to task-events-dlq for manual review.
Events that return 5xx status codes will be retried according to Dapr retry policy.
"""


# ============================================================================
# Factory Function
# ============================================================================

def create_task_completed_consumer(recurrence_handler) -> TaskCompletedConsumer:
    """
    Factory function to create TaskCompletedConsumer instance.

    Args:
        recurrence_handler: RecurrenceHandler instance

    Returns:
        TaskCompletedConsumer: Configured instance
    """
    return TaskCompletedConsumer(recurrence_handler)
