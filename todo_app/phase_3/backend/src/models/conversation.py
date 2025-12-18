"""
Conversation model for AI chatbot.
Phase 3 - Task 1.1 GREEN phase
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.message import Message


class Conversation(SQLModel, table=True):
    """Conversation entity for AI chat sessions."""

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: UUID = Field(index=True)  # Required field (no default, indexed)
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

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")
