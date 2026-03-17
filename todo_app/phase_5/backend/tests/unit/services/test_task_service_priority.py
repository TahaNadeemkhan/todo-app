import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from services.task_service import TaskService
from models.enums import Priority
from schemas.task_schemas import TaskCreate

@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session

@pytest.fixture
def mock_kafka_service():
    return AsyncMock()

@pytest.fixture
def service(mock_session, mock_kafka_service):
    # Pass mock_session where TaskService expects db_session
    svc = TaskService(mock_session, mock_kafka_service)
    # Mock the internal services to avoid side effects
    svc.recurrence_service = AsyncMock()
    svc.reminder_service = AsyncMock()
    return svc

@pytest.mark.asyncio
async def test_create_task_with_valid_priority(service, mock_session):
    task_data = TaskCreate(title="Test Task", priority=Priority.HIGH)
    user_id = "user123"
    
    result = await service.create_task(user_id, **task_data.model_dump())
    
    assert result.priority == Priority.HIGH
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called()

@pytest.mark.asyncio
async def test_create_task_default_priority(service, mock_session):
    task_data = TaskCreate(title="Test Task") # No priority specified
    user_id = "user123"
    
    result = await service.create_task(user_id, **task_data.model_dump())
    
    assert result.priority == Priority.MEDIUM
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called()
