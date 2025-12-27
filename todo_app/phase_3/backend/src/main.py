import os
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from chatkit.server import NonStreamingResult

logger = logging.getLogger(__name__)

from mcp_server.server import mcp_app
from db import get_async_session
from chatkit_store import DatabaseChatKitStore
from chatkit_server import TodoChatKitServer, TodoChatKitServerWithMCP
from api.routes import tasks, notifications

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
# Include notification API routes
app.include_router(notifications.router)

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
    - Gemini 2.5 Flash model for AI responses
    - Multilingual support (English + Urdu)
    """
    # Get Gemini API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}

    # Extract user_id from request headers (Better Auth JWT)
    # For development, use logged-in user's ID
    authorization = request.headers.get("Authorization", "")
    user_id = "XbN8PEmNydysjO4eQyFSV9bKNL6faSVe"  # Your actual user ID (tahanadeem2990@gmail.com)

    # TODO: Extract user_id from JWT token for production
    # if authorization.startswith("Bearer "):
    #     token = authorization[7:]
    #     user_id = extract_user_from_jwt(token)

    # Create database-backed store
    store = DatabaseChatKitStore(session)

    # Initialize ChatKit server with MCP tools integration
    chat_server = TodoChatKitServerWithMCP(store, api_key)

    # Handle ChatKit request with user context
    payload = await request.body()  # Get raw bytes for ChatKitServer
    result = await chat_server.process(payload, context=user_id)  # ✅ Pass user_id as context

    # Check if result is non-streaming (e.g., threads.list, threads.create)
    if isinstance(result, NonStreamingResult):
        # NonStreamingResult has a 'json' attribute with already-serialized JSON bytes
        # Just decode and parse it
        import json
        json_bytes = result.json
        json_str = json_bytes.decode('utf-8')
        result_dict = json.loads(json_str)

        # Debug: Log what's being sent to frontend
        logger.info(f"📤 Sending response to frontend (first 500 chars): {str(result_dict)[:500]}")

        return JSONResponse(content=result_dict)

    # Return streaming response for chat messages
    return StreamingResponse(result, media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
