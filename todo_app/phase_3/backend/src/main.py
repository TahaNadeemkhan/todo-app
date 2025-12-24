import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.server import mcp_app
from db import get_async_session
from chatkit_store import DatabaseChatKitStore
from chatkit_server import TodoChatKitServer, TodoChatKitServerWithMCP
from api.routes import tasks

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic if needed
    yield
    # Shutdown logic if needed

app = FastAPI(
    title="Todo Chatbot Phase 3",
    description="AI-Powered Todo Chatbot Backend with ChatKit Integration",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for ChatKit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task management API routes
app.include_router(tasks.router)

# We can also mount the MCP server if we want to expose it directly (optional)
# app.mount("/mcp", mcp_app)


@app.post("/chatkit", include_in_schema=False)
async def chatkit_endpoint(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """ChatKit endpoint with database-backed conversation storage.

    NOTE: This endpoint is designed for ChatKit React components.
    Do not test directly via Swagger - use the frontend ChatKit UI instead.

    This endpoint integrates OpenAI ChatKit with:
    - PostgreSQL database for persistent conversation storage
    - Gemini 2.0 Flash model for AI responses
    - Multilingual support (English + Urdu)
    """
    # Get Gemini API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}

    # Create database-backed store
    store = DatabaseChatKitStore(session)

    # Initialize ChatKit server with MCP tools integration
    chat_server = TodoChatKitServerWithMCP(store, api_key)

    # Handle ChatKit request
    payload = await request.body()
    result = await chat_server.process(payload, context="")

    return StreamingResponse(result, media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
