from typing import Optional
from sqlmodel import Field, SQLModel
import uuid

class TaskTagLink(SQLModel, table=True):
    """
    Join table for the many-to-many relationship between Task and Tag.
    """
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "tag_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
            }
        }
