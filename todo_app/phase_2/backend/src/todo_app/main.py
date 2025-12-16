"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from todo_app.config import get_settings
from todo_app.db import create_db_and_tables
from todo_app import models  # noqa: F401 - Import models to register with SQLModel

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # Startup: Create database tables
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created successfully!")
    yield
    # Shutdown: Cleanup if needed


from todo_app.routes import tasks
from todo_app.routes import notifications

app = FastAPI(
    title="Todo App API",
    description="Phase 2 - Full-Stack Web Application API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(notifications.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/debug/email-config", tags=["Debug"])
async def debug_email_config() -> dict:
    """Debug endpoint to check email configuration."""
    return {
        "email_configured": settings.email_configured,
        "use_brevo": settings.use_brevo,
        "has_brevo_key": bool(settings.brevo_api_key),
        "email_address": settings.email_address if settings.email_address else "NOT SET",
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "has_app_password": bool(settings.email_app_password),
    }


@app.get("/debug/test-email", tags=["Debug"])
async def test_email() -> dict:
    """Test email sending."""
    from todo_app.services.email_service import email_service

    if not settings.email_configured:
        return {"success": False, "error": "Email not configured"}

    try:
        result = await email_service.send_notification(
            to_email=settings.email_address,  # Send to self
            notification_type="task_created",
            task_title="Test Email from Railway",
            task_description="This is a test email to verify SMTP works on Railway.",
        )
        return {"success": result, "sent_to": settings.email_address}
    except Exception as e:
        return {"success": False, "error": str(e)}
