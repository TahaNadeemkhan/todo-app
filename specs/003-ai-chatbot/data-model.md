# Data Models: AI-Powered Todo Chatbot

**Date**: 2025-12-17
**Purpose**: Define database schema and domain models for conversation persistence

## Overview

Phase 3 introduces **2 new database models** to support stateless conversation management:
- **Conversation**: Represents a chat session between user and AI
- **Message**: Represents individual messages within a conversation

These models complement the existing **Task** model from Phase 2.

---

## 1. Conversation Model

### Entity Description

Represents a persistent chat session between a user and the AI assistant. Conversations have no explicit "closed" state - they remain open indefinitely and can be resumed at any time using the conversation_id.

### SQLModel Definition

```python
# backend/src/models/conversation.py
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.message import Message

class Conversation(SQLModel, table=True):
    """
    Represents a chat session between a user and the AI assistant.

    A conversation is created automatically when a user sends their first
    message without an existing conversation_id. The conversation persists
    across server restarts and can be resumed from any device.
    """
    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )

    # Foreign Keys
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this conversation (references Phase 2 users table)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this conversation was first created (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this conversation was last updated (UTC)"
    )

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174001",
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:15:00Z"
            }
        }
```

### Database Schema

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_conversations_user_id ON conversations(user_id)
);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_conversations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversations_updated_at
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION update_conversations_updated_at();
```

### Validation Rules

| Field | Rule | Enforcement |
|-------|------|-------------|
| `id` | Must be valid UUID | Database (UUID type) |
| `user_id` | Must exist in `users` table | Foreign key constraint |
| `created_at` | Must be UTC datetime | Application (default_factory) |
| `updated_at` | Must be UTC datetime | Application + DB trigger |

### Indexes

- **Primary Key**: `id` (UUID)
- **Foreign Key Index**: `user_id` - enables fast user conversation lookups

### Relationships

- **One-to-Many with Message**: A conversation has many messages (cascade delete)
- **Many-to-One with User**: A conversation belongs to one user (Phase 2 users table)

### State Transitions

Conversations do not have explicit states. They are created on first message and persist indefinitely.

**Lifecycle**:
1. **Created**: When user sends first message without conversation_id
2. **Active**: Any conversation with at least one message
3. **Resumed**: When user provides existing conversation_id in new request
4. **Deleted**: Only when user is deleted (CASCADE) or explicitly cleaned up

### Security Considerations

- **User Ownership**: All conversation queries MUST filter by `user_id` from JWT
- **Authorization**: Users can only access their own conversations
- **Privacy**: Conversation history contains sensitive user data; ensure proper access control

---

## 2. Message Model

### Entity Description

Represents a single message within a conversation. Messages are immutable once created and can be either user-generated or AI-generated (assistant).

### SQLModel Definition

```python
# backend/src/models/message.py
from sqlmodel import Field, SQLModel, Relationship, Column, Enum as SQLEnum
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.conversation import Conversation

class MessageRole(str, PyEnum):
    """
    Role of the message author.

    - USER: Message sent by the end user
    - ASSISTANT: Message generated by the AI agent
    """
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    """
    Represents a single message within a conversation.

    Messages are immutable once created. They preserve the complete
    conversation history for stateless AI agent context injection.
    """
    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Conversation this message belongs to"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of the conversation (denormalized for security)"
    )

    # Message Data
    role: MessageRole = Field(
        sa_column=Column(SQLEnum(MessageRole)),
        description="Who created this message: user or assistant"
    )
    content: str = Field(
        max_length=2000,
        description="Message text content (max 2000 chars per Assumption 9)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="When this message was created (UTC)"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "789e4567-e89b-12d3-a456-426614174002",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174001",
                "role": "user",
                "content": "Add task: Buy groceries",
                "created_at": "2025-12-17T10:00:00Z"
            }
        }
```

### Database Schema

```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant');

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL CHECK (char_length(content) <= 2000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_messages_conversation_created ON messages(conversation_id, created_at),
    INDEX idx_messages_user_id ON messages(user_id)
);

-- Constraint: content cannot be empty
ALTER TABLE messages
ADD CONSTRAINT content_not_empty CHECK (char_length(content) > 0);
```

### Validation Rules

| Field | Rule | Enforcement |
|-------|------|-------------|
| `id` | Must be valid UUID | Database (UUID type) |
| `conversation_id` | Must exist in `conversations` table | Foreign key constraint |
| `user_id` | Must exist in `users` table | Foreign key constraint |
| `user_id` | Must match conversation owner | Repository layer validation |
| `role` | Must be "user" or "assistant" | Enum constraint |
| `content` | Non-empty, max 2000 characters | Database CHECK + Pydantic |
| `created_at` | Must be UTC datetime | Application (default_factory) |

### Indexes

- **Primary Key**: `id` (UUID)
- **Composite Index**: `(conversation_id, created_at)` - enables fast conversation history retrieval ordered by time
- **Foreign Key Index**: `user_id` - enables user-level message queries

**Query Optimization**: The composite index `(conversation_id, created_at)` is critical for performance when fetching conversation history (last 50 messages).

### Relationships

- **Many-to-One with Conversation**: A message belongs to one conversation
- **Many-to-One with User**: A message belongs to one user (denormalized from conversation)

### State Transitions

Messages are **immutable** once created. They do not transition between states.

**Lifecycle**:
1. **Created**: When user sends message OR when AI generates response
2. **Persisted**: Message saved to database permanently
3. **Retrieved**: Fetched as part of conversation history
4. **Deleted**: Only when conversation or user is deleted (CASCADE)

### Security Considerations

- **User Ownership (Denormalized)**: `user_id` is stored on each message for fast security checks
- **Authorization**: Repository layer validates message.user_id matches conversation.user_id
- **Immutability**: Messages cannot be edited after creation (audit trail)

---

## 3. Data Model Relationships

### Entity-Relationship Diagram

```
┌─────────────┐
│    User     │ (Phase 2 - existing)
│             │
│ - id (PK)   │
│ - email     │
│ - name      │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼─────────────┐
│   Conversation     │ (Phase 3 - NEW)
│                    │
│ - id (PK)          │
│ - user_id (FK)     │◄──────────────┐
│ - created_at       │               │
│ - updated_at       │               │
└──────┬─────────────┘               │
       │                             │
       │ 1:N                         │
       │                             │
┌──────▼─────────────┐               │
│     Message        │ (Phase 3 - NEW)
│                    │               │
│ - id (PK)          │               │
│ - conversation_id (FK) ────────────┘
│ - user_id (FK)     │ (denormalized)
│ - role (enum)      │
│ - content          │
│ - created_at       │
└────────────────────┘

       ┌──────────────┐
       │    Task      │ (Phase 2 - existing)
       │              │
       │ - id (PK)    │
       │ - user_id (FK)
       │ - title      │
       │ - description│
       │ - completed  │
       └──────────────┘
       (No direct relationship to Conversation/Message)
```

### Cascade Behavior

- **User deleted** → All conversations deleted → All messages deleted
- **Conversation deleted** → All messages deleted
- **Message deleted** → No cascades (leaf entity)

---

## 4. Repository Interfaces

### ConversationRepository

```python
# backend/src/repositories/conversation_repository.py
from src.models.conversation import Conversation
from sqlmodel import select
from datetime import datetime

class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, user_id: UUID) -> Conversation:
        """Create a new conversation for a user"""
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: UUID, user_id: UUID) -> Conversation | None:
        """Get conversation by ID, ensuring it belongs to user"""
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, limit: int = 20) -> list[Conversation]:
        """List user's conversations, most recent first"""
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_timestamp(self, conversation_id: UUID):
        """Update conversation's updated_at timestamp (called when new message added)"""
        conversation = await self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            await self.session.commit()
```

### MessageRepository

```python
# backend/src/repositories/message_repository.py
from src.models.message import Message, MessageRole
from sqlmodel import select

class MessageRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: MessageRole,
        content: str
    ) -> Message:
        """Create a new message in a conversation"""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> list[Message]:
        """
        Get conversation history (last N messages) ordered by creation time.

        Args:
            conversation_id: Conversation to fetch messages from
            user_id: User ID for security validation
            limit: Max number of messages (default 50 per Assumption 6)

        Returns:
            List of messages ordered oldest to newest (for AI context injection)
        """
        query = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())  # Get most recent first
            .limit(limit)
        )
        result = await self.session.execute(query)
        messages = result.scalars().all()

        # Reverse to oldest-first for AI context injection
        return list(reversed(messages))
```

---

## 5. Data Migration Strategy

### Alembic Migration

```python
# backend/alembic/versions/xxx_add_conversation_and_message_tables.py
"""Add conversation and message tables

Revision ID: xxx
Revises: yyy  # Previous Phase 2 migration
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'xxx'
down_revision = 'yyy'  # Phase 2 migration ID

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create message_role enum
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant')")

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='message_role'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('char_length(content) > 0', name='content_not_empty'),
        sa.CheckConstraint('char_length(content) <= 2000', name='content_max_length'),
    )
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])

    # Trigger for auto-updating conversations.updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_conversations_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER conversations_updated_at
        BEFORE UPDATE ON conversations
        FOR EACH ROW
        EXECUTE FUNCTION update_conversations_updated_at();
    """)

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
    op.execute("DROP TYPE message_role")
    op.execute("DROP FUNCTION update_conversations_updated_at()")
```

### Migration Execution

```bash
# Generate migration
cd backend
uv run alembic revision --autogenerate -m "Add conversation and message tables"

# Apply migration
uv run alembic upgrade head

# Verify
uv run alembic current
```

---

## 6. Testing Considerations

### Unit Tests

```python
# tests/unit/models/test_conversation.py
def test_conversation_creation():
    """Test conversation model instantiation"""
    conversation = Conversation(user_id=user_id)
    assert conversation.id is not None
    assert conversation.user_id == user_id
    assert conversation.created_at is not None
    assert conversation.updated_at is not None

# tests/unit/models/test_message.py
def test_message_validation():
    """Test message content validation"""
    with pytest.raises(ValidationError):
        Message(
            conversation_id=conv_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=""  # Empty content should fail
        )

    with pytest.raises(ValidationError):
        Message(
            conversation_id=conv_id,
            user_id=user_id,
            role=MessageRole.USER,
            content="x" * 2001  # Exceeds max length
        )
```

### Repository Tests

```python
# tests/unit/repositories/test_conversation_repository.py
async def test_get_conversation_validates_ownership():
    """Test that get_by_id validates user ownership"""
    # Arrange
    conversation = await conversation_repository.create(user_id=owner_id)

    # Act & Assert
    result = await conversation_repository.get_by_id(conversation.id, user_id=attacker_id)
    assert result is None  # Attacker can't access owner's conversation

# tests/unit/repositories/test_message_repository.py
async def test_get_conversation_history_orders_correctly():
    """Test that history is returned oldest-first"""
    # Arrange
    await message_repository.create(conv_id, user_id, MessageRole.USER, "First")
    await message_repository.create(conv_id, user_id, MessageRole.ASSISTANT, "Second")
    await message_repository.create(conv_id, user_id, MessageRole.USER, "Third")

    # Act
    history = await message_repository.get_conversation_history(conv_id, user_id)

    # Assert
    assert len(history) == 3
    assert history[0].content == "First"
    assert history[1].content == "Second"
    assert history[2].content == "Third"
```

---

## Summary

### New Database Entities

1. **Conversation**: Persistent chat sessions
   - 1:N relationship with Message
   - N:1 relationship with User (Phase 2)
   - Auto-managed timestamps with DB trigger

2. **Message**: Individual chat messages
   - Immutable once created
   - Strict role enum (user/assistant)
   - Optimized composite index for history retrieval

### Key Design Decisions

- **Denormalized user_id in Message**: Enables fast security validation without JOIN
- **Composite index on (conversation_id, created_at)**: Optimizes conversation history queries
- **50 message limit**: Balances context richness with performance (Assumption 6)
- **Cascade deletes**: User deletion removes all conversations and messages
- **Immutable messages**: Audit trail for conversation history

### Next Steps

1. Create API contracts directory and files
2. Generate quickstart.md for developer onboarding
3. Run agent context update script
4. Proceed to `/sp.tasks` for implementation task generation
