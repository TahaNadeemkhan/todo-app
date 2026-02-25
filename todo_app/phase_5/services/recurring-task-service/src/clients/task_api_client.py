"""
TaskApiClient - HTTP client for calling backend API via Dapr service invocation

Provides abstraction for creating tasks via backend API.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx


logger = logging.getLogger(__name__)


class TaskApiClient:
    """
    HTTP client for calling backend API to create tasks.

    Uses Dapr service invocation for service-to-service communication.
    """

    def __init__(self, backend_url: str, use_dapr: bool = True):
        """
        Initialize TaskApiClient.

        Args:
            backend_url: Backend API base URL (or Dapr sidecar URL)
            use_dapr: Whether to use Dapr service invocation (default: True)
        """
        self.backend_url = backend_url.rstrip("/")
        self.use_dapr = use_dapr

        # Dapr service invocation URL format:
        # http://localhost:3500/v1.0/invoke/{app-id}/method/{method-name}
        if use_dapr:
            self.dapr_url = "http://localhost:3500/v1.0/invoke/backend-api/method"
        else:
            self.dapr_url = None

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_at: Optional[str] = None,
        has_recurrence: bool = False,
        recurrence_pattern: Optional[str] = None,
        recurrence_interval: Optional[int] = None,
        recurrence_days_of_week: Optional[List[int]] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new task via backend API.

        Args:
            user_id: User UUID
            title: Task title
            description: Task description (optional)
            priority: Task priority (high/medium/low)
            tags: Task tags (optional)
            due_at: Task due date/time in ISO 8601 format (optional)
            has_recurrence: Whether task recurs (optional)
            recurrence_pattern: Recurrence pattern (daily/weekly/monthly)
            recurrence_interval: Recurrence interval
            recurrence_days_of_week: Days of week for weekly recurrence
            recurrence_day_of_month: Day of month for monthly recurrence

        Returns:
            Dict: Created task response from API

        Raises:
            httpx.HTTPError: If API call fails
        """
        # Build request payload
        payload = {
            "title": title,
            "description": description,
            "priority": priority,
            "tags": tags or [],
            "due_date": due_at,  # Backend expects 'due_date' field
            "has_recurrence": has_recurrence,
        }

        # Add recurrence fields if applicable
        if has_recurrence:
            payload["recurrence_pattern"] = recurrence_pattern
            payload["recurrence_interval"] = recurrence_interval

            if recurrence_days_of_week:
                payload["recurrence_days_of_week"] = recurrence_days_of_week
            if recurrence_day_of_month:
                payload["recurrence_day_of_month"] = recurrence_day_of_month

        # Construct API endpoint URL
        if self.use_dapr and self.dapr_url:
            # Dapr service invocation
            url = f"{self.dapr_url}/api/{user_id}/tasks"
            logger.debug(f"Calling backend via Dapr: {url}")
        else:
            # Direct HTTP call
            url = f"{self.backend_url}/api/{user_id}/tasks"
            logger.debug(f"Calling backend directly: {url}")

        # Make HTTP POST request
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                created_task = response.json()

                logger.info(
                    f"Task created via API: task_id={created_task.get('id')}, "
                    f"user_id={user_id}, title={title}"
                )

                return created_task

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"API error creating task: status={e.response.status_code}, "
                    f"body={e.response.text}"
                )
                raise

            except httpx.RequestError as e:
                logger.error(
                    f"Network error creating task: {str(e)}"
                )
                raise
