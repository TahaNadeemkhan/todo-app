"""
T072: Contract test for POST /tasks with recurrence fields
TDD Red Phase - This test will FAIL until recurrence API is implemented

Tests that the API accepts recurrence parameters and returns correct response.
"""

import pytest
from httpx import AsyncClient


class TestTaskRecurrenceAPIContract:
    """Contract tests for task creation with recurrence."""

    @pytest.mark.asyncio
    async def test_create_task_with_daily_recurrence(self, async_client: AsyncClient):
        """Test POST /tasks with daily recurrence pattern."""
        user_id = "test-user-123"

        task_data = {
            "title": "Daily standup",
            "description": "Team standup meeting",
            "priority": "high",
            "tags": ["meetings"],
            "has_recurrence": True,
            "recurrence_pattern": "daily",
            "recurrence_interval": 1
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        # Assert response
        assert response.status_code == 201
        created_task = response.json()

        # Verify recurrence fields in response
        assert created_task["has_recurrence"] is True
        assert created_task["recurrence_pattern"] == "daily"
        assert created_task["recurrence_interval"] == 1

    @pytest.mark.asyncio
    async def test_create_task_with_weekly_recurrence(self, async_client: AsyncClient):
        """Test POST /tasks with weekly recurrence pattern."""
        user_id = "test-user-123"

        task_data = {
            "title": "Team sync",
            "description": "Weekly team sync meeting",
            "priority": "medium",
            "tags": ["meetings"],
            "has_recurrence": True,
            "recurrence_pattern": "weekly",
            "recurrence_interval": 1,
            "recurrence_days_of_week": [0, 3, 5]  # Monday, Thursday, Saturday
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        assert response.status_code == 201
        created_task = response.json()

        assert created_task["recurrence_pattern"] == "weekly"
        assert created_task["recurrence_days_of_week"] == [0, 3, 5]

    @pytest.mark.asyncio
    async def test_create_task_with_monthly_recurrence(self, async_client: AsyncClient):
        """Test POST /tasks with monthly recurrence pattern."""
        user_id = "test-user-123"

        task_data = {
            "title": "Monthly report",
            "description": "Submit monthly status report",
            "priority": "high",
            "tags": ["reports"],
            "has_recurrence": True,
            "recurrence_pattern": "monthly",
            "recurrence_interval": 1,
            "recurrence_day_of_month": 1  # 1st of every month
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        assert response.status_code == 201
        created_task = response.json()

        assert created_task["recurrence_pattern"] == "monthly"
        assert created_task["recurrence_day_of_month"] == 1

    @pytest.mark.asyncio
    async def test_create_task_without_recurrence(self, async_client: AsyncClient):
        """Test POST /tasks without recurrence (backward compatibility)."""
        user_id = "test-user-123"

        task_data = {
            "title": "One-time task",
            "description": "This task does not recur",
            "priority": "low",
            "tags": []
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        assert response.status_code == 201
        created_task = response.json()

        # Default values for recurrence
        assert created_task.get("has_recurrence", False) is False
        assert created_task.get("recurrence_pattern") is None

    @pytest.mark.asyncio
    async def test_get_task_recurrence_info(self, async_client: AsyncClient):
        """T083: Test GET /tasks/{id}/recurrence endpoint."""
        user_id = "test-user-123"

        # First create a recurring task
        task_data = {
            "title": "Weekly review",
            "priority": "medium",
            "has_recurrence": True,
            "recurrence_pattern": "weekly",
            "recurrence_interval": 1,
            "recurrence_days_of_week": [0, 4]  # Monday, Friday
        }

        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )
        task_id = create_response.json()["id"]

        # Get recurrence info
        recurrence_response = await async_client.get(
            f"/api/{user_id}/tasks/{task_id}/recurrence"
        )

        assert recurrence_response.status_code == 200
        recurrence_info = recurrence_response.json()

        assert recurrence_info["pattern"] == "weekly"
        assert recurrence_info["interval"] == 1
        assert recurrence_info["days_of_week"] == [0, 4]
        assert recurrence_info["active"] is True
        assert "next_due_at" in recurrence_info

    @pytest.mark.asyncio
    async def test_stop_task_recurrence(self, async_client: AsyncClient):
        """T084: Test DELETE /tasks/{id}/recurrence endpoint."""
        user_id = "test-user-123"

        # Create a recurring task
        task_data = {
            "title": "Daily backup",
            "priority": "high",
            "has_recurrence": True,
            "recurrence_pattern": "daily",
            "recurrence_interval": 1
        }

        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )
        task_id = create_response.json()["id"]

        # Stop recurrence
        delete_response = await async_client.delete(
            f"/api/{user_id}/tasks/{task_id}/recurrence"
        )

        assert delete_response.status_code == 200
        result = delete_response.json()
        assert result["message"] == "Recurrence stopped successfully"

        # Verify recurrence is inactive
        recurrence_response = await async_client.get(
            f"/api/{user_id}/tasks/{task_id}/recurrence"
        )
        recurrence_info = recurrence_response.json()
        assert recurrence_info["active"] is False

    @pytest.mark.asyncio
    async def test_create_task_invalid_recurrence_pattern(self, async_client: AsyncClient):
        """Test that invalid recurrence pattern is rejected."""
        user_id = "test-user-123"

        task_data = {
            "title": "Invalid task",
            "has_recurrence": True,
            "recurrence_pattern": "yearly",  # Not supported (only daily/weekly/monthly)
            "recurrence_interval": 1
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == 422
        error = response.json()
        assert "recurrence_pattern" in str(error).lower()

    @pytest.mark.asyncio
    async def test_create_task_weekly_without_days_of_week(self, async_client: AsyncClient):
        """Test that weekly recurrence requires days_of_week."""
        user_id = "test-user-123"

        task_data = {
            "title": "Invalid weekly task",
            "has_recurrence": True,
            "recurrence_pattern": "weekly",
            "recurrence_interval": 1
            # Missing recurrence_days_of_week
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        # Should return 422 (validation error)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_monthly_without_day_of_month(self, async_client: AsyncClient):
        """Test that monthly recurrence requires day_of_month."""
        user_id = "test-user-123"

        task_data = {
            "title": "Invalid monthly task",
            "has_recurrence": True,
            "recurrence_pattern": "monthly",
            "recurrence_interval": 1
            # Missing recurrence_day_of_month
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data
        )

        # Should return 422 (validation error)
        assert response.status_code == 422
