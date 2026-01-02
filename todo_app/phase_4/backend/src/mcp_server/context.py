from uuid import UUID
from pydantic import BaseModel, Field

class ToolContext(BaseModel):
    """Context passed to MCP tools."""
    authenticated_user_id: UUID = Field(..., description="The ID of the currently authenticated user")
    request_id: str = Field(..., description="Unique request identifier for tracing")
