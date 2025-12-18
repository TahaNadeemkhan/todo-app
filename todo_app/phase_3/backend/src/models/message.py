"""
Message model for AI chatbot conversations.
Phase 3 - Task 1.2 GREEN phase
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, Enum as SQLEnum, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.conversation import Conversation


class MessageRole(str, PyEnum):
    """Enum for message role (user or assistant)."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message entity for conversation history."""

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        index=True,
        foreign_key="conversations.id",
        description="Conversation this message belongs to"
    )
    user_id: UUID = Field(
        index=True,
        description="User who owns this message (FK to users.id from Phase 2)"
    )
    role: MessageRole = Field(
        sa_column=Column(SQLEnum(MessageRole)),
        description="Message role (user or assistant)"
    )
    content: str = Field(
        max_length=2000,
        description="Message content text"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,  # Indexed for temporal queries
        description="Message creation timestamp"
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
