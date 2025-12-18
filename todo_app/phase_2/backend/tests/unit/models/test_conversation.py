"""
Unit tests for Conversation model (TDD - RED phase).
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import ValidationError
from todo_app.models import Conversation


def test_conversation_creation():
    """Test conversation model instantiation with required fields"""
    user_id = str(uuid4())
    conversation = Conversation(user_id=user_id)

    assert conversation.id is not None
    assert conversation.user_id == user_id
    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_requires_user_id():
    """Test conversation creation fails without user_id"""
    with pytest.raises(ValidationError):
        Conversation()


def test_conversation_timestamps_auto_generated():
    """Test created_at and updated_at are auto-generated"""
    user_id = str(uuid4())
    conversation = Conversation(user_id=user_id)

    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    # Both should be very close to now
    assert (datetime.now(conversation.created_at.tzinfo) - conversation.created_at).total_seconds() < 1


def test_conversation_user_id_indexed():
    """Test user_id field has index for efficient queries"""
    # This is a schema-level test; we verify the Field definition
    from sqlmodel import Field

    # Get the Field metadata for user_id
    user_id_field = Conversation.__fields__['user_id']
    assert user_id_field.field_info.extra.get('index', False) is True


def test_conversation_table_name():
    """Test conversation uses correct table name"""
    assert Conversation.__tablename__ == "conversations"
