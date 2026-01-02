from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database (Default to a valid dummy for testing/mocking if env is missing)
    database_url: str = "sqlite+aiosqlite:///dummy.db" 

    # Authentication
    better_auth_secret: str = "dummy_secret"

    # OpenAI
    openai_api_key: str = "dummy_key"
    openai_model: str = "gpt-4"

    # Email Settings
    email_address: str = ""
    email_app_password: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    brevo_api_key: str = ""
    
    # Internal service URLs if needed
    email_service_url: str = "http://localhost:8001"

    @property
    def email_configured(self) -> bool:
        """Check if email is properly configured (Brevo or SMTP)."""
        return bool(self.brevo_api_key) or bool(self.email_address and self.email_app_password)

    @property
    def use_brevo(self) -> bool:
        """Use Brevo API if configured."""
        return bool(self.brevo_api_key)

@lru_cache
def get_settings() -> Settings:
    return Settings()