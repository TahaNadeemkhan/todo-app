from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from services.chat_service import ChatService
from db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    tool_calls: List[Dict[str, Any]]
    created_at: datetime

# TODO: Add JWT authentication dependency here (Task T035 integration)
# For now, we trust the path parameter as per current scope, but in prod verify JWT matches path param

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Chat with the AI Todo Assistant.
    """
    service = ChatService(session)
    
    try:
        result = await service.process_message(
            user_id=user_id,
            message_content=request.message,
            conversation_id=request.conversation_id
        )
        return ChatResponse(**result)
    except Exception as e:
        # Log the full error here
        print(f"Chat Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
