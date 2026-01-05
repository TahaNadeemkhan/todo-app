import os
import logging
from fastapi import FastAPI, Request, Depends, HTTPException
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

from fastapi import File, UploadFile
import base64
import httpx

@app.post("/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio using Gemini 2.5 Flash.
    """
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")

        if gemini_key:
            logger.info("🎙️ Using Gemini 2.5 Flash for transcription")
            
            # Read file bytes directly
            file.file.seek(0)
            audio_bytes = file.file.read()
            b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

            # Use the available model from user's list
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Please transcribe this audio file exactly. Return ONLY the transcribed text, no other commentary."},
                        {"inline_data": {
                            "mime_type": "audio/webm", # or match file.content_type if reliable
                            "data": b64_audio
                        }}
                    ]
                }]
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=30.0)
                
                if resp.status_code != 200:
                    logger.error(f"Gemini API Error: {resp.status_code} - {resp.text}")
                    return JSONResponse(status_code=500, content={"error": f"Gemini STT failed: {resp.text}"})
                
                result = resp.json()
                # Extract text from Gemini response structure
                try:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return {"text": text.strip()}
                except (KeyError, IndexError) as e:
                    logger.error(f"Failed to parse Gemini response: {result}")
                    return JSONResponse(status_code=500, content={"error": "Invalid Gemini response format"})

        else:
            return JSONResponse(status_code=500, content={"error": "GEMINI_API_KEY not found"})

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


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

    # ✅ CRITICAL: Extract user_id from ChatKit request context
    # The Next.js API route injects user_id from Better Auth session into context field
    payload_bytes = await request.body()
    payload_str = payload_bytes.decode('utf-8')
    import json
    payload_dict = json.loads(payload_str)

    # Get user_id from context field (injected by Next.js API route)
    user_id = payload_dict.get("context")

    if user_id:
        logger.info(f"✅ User context from request: {user_id}")
    else:
        # DEVELOPMENT FALLBACK
        logger.warning(f"⚠️ No context in request, using fallback user")
        user_id = "XbN8PEmNydysjO4eQyFSV9bKNL6faSVe"
        logger.info(f"🔧 DEV MODE: Using fallback user_id: {user_id}")

    # Create database-backed store
    store = DatabaseChatKitStore(session)

    # Initialize ChatKit server with MCP tools integration
    chat_server = TodoChatKitServerWithMCP(store, api_key)

    # Handle ChatKit request with user context
    result = await chat_server.process(payload_bytes, context=user_id)  # ✅ Pass user_id as context

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
