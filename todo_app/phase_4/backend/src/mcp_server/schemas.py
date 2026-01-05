from uuid import UUID
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

# --- Add Task ---
class AddTaskInput(BaseModel):
    user_id: UUID = Field(..., description="User ID (must match authenticated user)")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description")

class AddTaskOutput(BaseModel):
    task_id: UUID
    status: Literal["created"]
    title: str
    email_sent: bool = Field(False, description="Whether email notification was sent")

# --- List Tasks ---
class ListTasksInput(BaseModel):
    user_id: UUID = Field(..., description="User ID (must match authenticated user)")
    status: Literal["all", "pending", "completed"] = Field("all", description="Filter tasks by status")

class TaskSchema(BaseModel):
    task_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: str  # ISO format string

class ListTasksOutput(BaseModel):
    tasks: List[TaskSchema]
    count: int

# --- Complete Task ---
class CompleteTaskInput(BaseModel):
    user_id: UUID = Field(..., description="User ID (must match authenticated user)")
    task_id: UUID = Field(..., description="Task ID to mark as completed")

class CompleteTaskOutput(BaseModel):
    task_id: UUID
    status: Literal["completed"]
    title: str

# --- Delete Task ---
class DeleteTaskInput(BaseModel):
    user_id: UUID = Field(..., description="User ID (must match authenticated user)")
    task_id: UUID = Field(..., description="Task ID to delete")

class DeleteTaskOutput(BaseModel):
    task_id: UUID
    status: Literal["deleted"]

# --- Update Task ---
class UpdateTaskInput(BaseModel):
    user_id: UUID = Field(..., description="User ID (must match authenticated user)")
    task_id: UUID = Field(..., description="Task ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")

class UpdateTaskOutput(BaseModel):
    task_id: UUID
    status: Literal["updated"]
    title: str
    description: Optional[str]
