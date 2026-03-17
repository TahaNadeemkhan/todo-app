"""
Configuration settings for notification-service.
Loads from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str

    # Email - Brevo API (Production)
    brevo_api_key: str | None = None

    # Email - SMTP (Local Development Fallback)
    smtp_host: str = "smtp-relay.brevo.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "noreply@itasks.app"
    smtp_from_name: str = "iTasks Reminders"

    # Firebase Cloud Messaging (Push Notifications)
    fcm_credentials_json: str | None = None
    fcm_project_id: str | None = None

    # Dapr
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001
    dapr_app_id: str = "notification-service"
    dapr_pubsub_name: str = "pubsub-kafka"
    dapr_reminders_topic: str = "reminders"
    dapr_notifications_topic: str = "notifications"

    # Service Configuration
    service_port: int = 8002
    log_level: str = "INFO"

    # Retry Policy
    max_retry_attempts: int = 3
    retry_backoff_base: float = 2.0  # Exponential backoff: 2^attempt seconds
    retry_backoff_max: int = 300  # Max 5 minutes between retries

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def use_brevo(self) -> bool:
        """Check if Brevo API is configured."""
        return self.brevo_api_key is not None and self.brevo_api_key != ""

    @property
    def email_configured(self) -> bool:
        """Check if any email method is configured."""
        return self.use_brevo or (
            self.smtp_username is not None
            and self.smtp_password is not None
        )

    @property
    def fcm_configured(self) -> bool:
        """Check if FCM is configured."""
        return (
            self.fcm_credentials_json is not None
            and self.fcm_project_id is not None
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
