import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

from models.task_tag_link import TaskTagLink # Keep direct import for link_model

if TYPE_CHECKING:
    from models.task import Task

class Tag(SQLModel, table=True):
    """
    Represents a tag that can be associated with tasks.
    User-scoped tags, allowing users to define their own categorization.
    """
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, max_length=50) # Tag name, e.g., "work", "personal"
    user_id: str = Field(index=True) # User who owns this tag
    color: Optional[str] = Field(default=None, max_length=7) # Hex color code for UI, e.g., "#FF0000"

    # Relationship to tasks via the link model
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "name": "work",
                "user_id": "user123",
                "color": "#4CAF50"
            }
        }
