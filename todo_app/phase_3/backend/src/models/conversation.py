"""
Conversation model for AI chatbot.
Phase 3 - Task 1.1 GREEN phase
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.message import Message


class Conversation(SQLModel, table=True):
    """Conversation entity for AI chat sessions."""

    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(index=True)  # Required field (no default, indexed)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Last update timestamp"
    )

    # Relationship to messages (will be defined in Task 1.2)
    # messages: list["Message"] = Relationship(back_populates="conversation")
