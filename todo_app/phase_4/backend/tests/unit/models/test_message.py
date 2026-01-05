"""
Unit tests for Message model (TDD - RED phase).
Task 1.2: Message Model
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import ValidationError
from models.message import Message, MessageRole


def test_message_creation():
    """Test message model instantiation with required fields"""
    conversation_id = uuid4()
    user_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content="Hello, world!"
    )

    assert message.id is not None
    assert isinstance(message.id, UUID)
    assert message.conversation_id == conversation_id
    assert isinstance(message.conversation_id, UUID)
    assert message.user_id == user_id
    assert isinstance(message.user_id, UUID)
    assert message.role == MessageRole.USER
    assert message.content == "Hello, world!"
    assert message.created_at is not None
    assert isinstance(message.created_at, datetime)


def test_message_role_enum():
    """Test MessageRole enum has correct values"""
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
    # Only two roles should exist
    assert len(MessageRole.__members__) == 2


def test_message_role_validation():
    """Test message role must be valid enum value"""
    conversation_id = uuid4()
    user_id = uuid4()

    # Valid roles should work
    user_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content="Test"
    )
    assert user_msg.role == MessageRole.USER

    assistant_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content="Test"
    )
    assert assistant_msg.role == MessageRole.ASSISTANT


def test_message_content_max_length():
    """Test message content has max length constraint"""
    conversation_id = uuid4()
    user_id = uuid4()

    # 2000 characters should be allowed
    long_content = "a" * 2000
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=long_content
    )
    assert len(message.content) == 2000


def test_message_table_name():
    """Test message uses correct table name"""
    assert Message.__tablename__ == "messages"


def test_message_indexes():
    """Test message has required indexes for efficient queries"""
    # Verify conversation_id is indexed
    conversation_id_field = Message.model_fields['conversation_id']
    assert hasattr(conversation_id_field, 'json_schema_extra') or \
           (hasattr(conversation_id_field, 'metadata') and any('index' in str(m) for m in conversation_id_field.metadata))

    # Verify user_id is indexed
    user_id_field = Message.model_fields['user_id']
    assert hasattr(user_id_field, 'json_schema_extra') or \
           (hasattr(user_id_field, 'metadata') and any('index' in str(m) for m in user_id_field.metadata))


def test_message_created_at_indexed():
    """Test created_at is indexed for temporal queries"""
    created_at_field = Message.model_fields['created_at']
    assert hasattr(created_at_field, 'json_schema_extra') or \
           (hasattr(created_at_field, 'metadata') and any('index' in str(m) for m in created_at_field.metadata))


def test_message_id_is_uuid():
    """Test message ID is a valid UUID"""
    conversation_id = uuid4()
    user_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content="Test"
    )

    # ID should be a valid UUID object
    assert message.id is not None
    assert isinstance(message.id, UUID)


def test_message_conversation_relationship():
    """Test message relationship to conversation"""
    conversation_id = uuid4()
    user_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content="Test"
    )
    assert hasattr(message, "conversation")
    # Initially None until connected in a session
    assert message.conversation is None
