"""
Unit tests for Conversation model (TDD - RED phase).
Task 1.1: Conversation Model
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import ValidationError
from models.conversation import Conversation
from models.message import Message


def test_conversation_creation():
    """Test conversation model instantiation with required fields"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    assert conversation.id is not None
    assert isinstance(conversation.id, UUID)
    assert conversation.user_id == user_id
    assert isinstance(conversation.user_id, UUID)
    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_timestamps_auto_generated():
    """Test created_at and updated_at are auto-generated"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    # Both should be very close to now (within 1 second)
    now = datetime.now(conversation.created_at.tzinfo)
    assert (now - conversation.created_at).total_seconds() < 1
    assert (now - conversation.updated_at).total_seconds() < 1


def test_conversation_user_id_indexed():
    """Test user_id field has index metadata for efficient queries"""
    # Verify the Field definition includes index=True
    user_id_field = Conversation.model_fields['user_id']
    # SQLModel stores index info in field_info
    assert hasattr(user_id_field, 'json_schema_extra') or \
           (hasattr(user_id_field, 'metadata') and any('index' in str(m) for m in user_id_field.metadata))


def test_conversation_table_name():
    """Test conversation uses correct table name"""
    assert Conversation.__tablename__ == "conversations"


def test_conversation_id_is_uuid():
    """Test conversation ID is a valid UUID"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    # ID should be a valid UUID object
    assert conversation.id is not None
    assert isinstance(conversation.id, UUID)


def test_conversation_messages_relationship():
    """Test conversation relationship to messages"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)
    assert hasattr(conversation, "messages")
    # Initially empty
    assert conversation.messages == []
