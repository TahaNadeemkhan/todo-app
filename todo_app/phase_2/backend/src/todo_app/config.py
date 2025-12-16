"""
Application configuration using Pydantic Settings.
Loads environment variables with validation.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Email Settings (Legacy SMTP - for local dev)
    email_address: str = ""
    email_app_password: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    # Resend API (for production - Railway blocks SMTP)
    resend_api_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def email_configured(self) -> bool:
        """Check if email is properly configured (Resend or SMTP)."""
        return bool(self.resend_api_key) or bool(self.email_address and self.email_app_password)

    @property
    def use_resend(self) -> bool:
        """Use Resend API if configured."""
        return bool(self.resend_api_key)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
