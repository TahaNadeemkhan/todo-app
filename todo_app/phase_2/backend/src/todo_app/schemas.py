"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
