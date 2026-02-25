import pytest
import uuid
from models.tag import Tag
from models.task_tag_link import TaskTagLink

def test_create_tag():
    """Test creating a tag instance."""
    tag_id = uuid.uuid4()
    tag = Tag(
        id=tag_id,
        name="work",
        user_id="user123",
        color="#4CAF50"
    )
    assert tag.id == tag_id
    assert tag.name == "work"
    assert tag.user_id == "user123"
    assert tag.color == "#4CAF50"

def test_tag_default_id():
    """Test that tag generates a default UUID."""
    tag = Tag(name="personal", user_id="user123")
    assert isinstance(tag.id, uuid.UUID)

def test_create_task_tag_link():
    """Test creating a TaskTagLink instance."""
    task_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    link = TaskTagLink(task_id=task_id, tag_id=tag_id)
    assert link.task_id == task_id
    assert link.tag_id == tag_id
