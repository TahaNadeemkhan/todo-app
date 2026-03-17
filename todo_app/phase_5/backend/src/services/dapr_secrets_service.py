"""
T059-T061: DaprSecretsService - Dapr Secrets Store abstraction

Provides portable secrets management using Dapr Secrets API.
Abstracts Kubernetes Secrets/HashiCorp Vault/AWS Secrets Manager/Azure Key Vault.

Use Cases:
- T060: Load configuration secrets (DATABASE_URL, JWT_SECRET, API keys)
- T061: Database connection credentials
- SMTP credentials
- Third-party API tokens
"""

import logging
import os
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class DaprSecretsService:
    """
    T059: Dapr Secrets Store service for portable secrets management using HTTP API.
    Bypasses Dapr SDK for compatibility with Python 3.13.
    """

    def __init__(
        self,
        dapr_http_port: str = "3500",
        secret_store_name: str = "kubernetes-secrets"
    ):
        """
        Initialize DaprSecretsService.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
            secret_store_name: Dapr secret store component name (default: kubernetes-secrets)
        """
        port = os.getenv("DAPR_HTTP_PORT", dapr_http_port)
        self.dapr_url = f"http://localhost:{port}/v1.0/secrets/{secret_store_name}"
        self.secret_store_name = secret_store_name

        logger.info(f"DaprSecretsService (HTTP) initialized: store={secret_store_name} at {self.dapr_url}")

    async def get_secret(
        self,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Get secret value by key using Dapr HTTP API.
        """
        try:
            url = f"{self.dapr_url}/{key}"
            params = metadata or {}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                
                if response.status_code == 404:
                    logger.warning(f"Secret not found: key={key}")
                    return None
                
                response.raise_for_status()
                secret_dict = response.json()

                # Dapr returns secrets as dict {key: value}
                secret_value = secret_dict.get(key)

                logger.info(f"Secret retrieved: key={key}, store={self.secret_store_name}")
                return secret_value

        except Exception as e:
            logger.error(f"Dapr secret get failed: key={key}, error={str(e)}")
            # Fallback to environment variables for local/hybrid scenarios
            env_value = os.getenv(key)
            if env_value:
                logger.info(f"Falling back to env var for {key}")
                return env_value
            raise Exception(f"Failed to get secret '{key}': {str(e)}") from e

    async def get_bulk_secrets(
        self,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Get all secrets from the secret store. (Note: Dapr bulk secrets API might vary)
        """
        try:
            url = f"{self.dapr_url}/bulk"
            params = metadata or {}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                bulk_response = response.json()

                # Flatten nested dict structure { "key": { "key": "value" } }
                secrets = {}
                for key, value_dict in bulk_response.items():
                    if isinstance(value_dict, dict):
                        secrets[key] = value_dict.get(key, "")
                    else:
                        secrets[key] = value_dict

                logger.info(f"Bulk secrets retrieved: count={len(secrets)}, store={self.secret_store_name}")
                return secrets

        except Exception as e:
            logger.error(f"Dapr bulk secret get failed: error={str(e)}")
            return {}

    def close(self) -> None:
        """Close resources."""
        pass


# ============================================================================
# T060: Configuration Loader using Dapr Secrets
# ============================================================================

class SecretConfig:
    """
    T060: Configuration class that loads secrets via Dapr.

    Usage:
        config = SecretConfig()
        await config.load_secrets()
        db_url = config.database_url
        jwt_secret = config.jwt_secret
    """

    def __init__(self, secret_store_name: str = "secretstore"):
        """
        Initialize SecretConfig.

        Args:
            secret_store_name: Dapr secret store component name
        """
        self.secrets_service = DaprSecretsService(secret_store_name=secret_store_name)

        # Secret values (loaded on-demand)
        self.database_url: Optional[str] = None
        self.jwt_secret: Optional[str] = None
        self.smtp_host: Optional[str] = None
        self.smtp_port: Optional[int] = None
        self.smtp_user: Optional[str] = None
        self.smtp_password: Optional[str] = None
        self.fcm_server_key: Optional[str] = None
        self.openai_api_key: Optional[str] = None

    async def load_secrets(self) -> None:
        """
        T060: Load all required secrets from Dapr Secrets Store.

        This should be called during application startup.

        Raises:
            Exception: If any required secret is missing
        """
        logger.info("Loading secrets from Dapr...")

        try:
            # Load all secrets in bulk (more efficient)
            secrets = await self.secrets_service.get_bulk_secrets()

            # Extract required secrets
            self.database_url = secrets.get("database-url") or secrets.get("DATABASE_URL")
            self.jwt_secret = secrets.get("jwt-secret") or secrets.get("JWT_SECRET")
            self.smtp_host = secrets.get("smtp-host") or secrets.get("SMTP_HOST")
            self.smtp_port = int(secrets.get("smtp-port") or secrets.get("SMTP_PORT") or "587")
            self.smtp_user = secrets.get("smtp-user") or secrets.get("SMTP_USER")
            self.smtp_password = secrets.get("smtp-password") or secrets.get("SMTP_PASSWORD")
            self.fcm_server_key = secrets.get("fcm-server-key") or secrets.get("FCM_SERVER_KEY")
            self.openai_api_key = secrets.get("openai-api-key") or secrets.get("OPENAI_API_KEY")

            # Validate required secrets
            if not self.database_url:
                raise ValueError("Required secret 'database-url' not found")
            if not self.jwt_secret:
                raise ValueError("Required secret 'jwt-secret' not found")

            logger.info("Secrets loaded successfully from Dapr")

        except Exception as e:
            logger.error(f"Failed to load secrets: {str(e)}")
            raise

    def get_database_url(self) -> str:
        """
        T061: Get database connection URL.

        Returns:
            Database URL string

        Raises:
            ValueError: If database URL not loaded
        """
        if not self.database_url:
            raise ValueError("Database URL not loaded. Call load_secrets() first.")
        return self.database_url

    def get_jwt_secret(self) -> str:
        """
        Get JWT secret for token signing.

        Returns:
            JWT secret string

        Raises:
            ValueError: If JWT secret not loaded
        """
        if not self.jwt_secret:
            raise ValueError("JWT secret not loaded. Call load_secrets() first.")
        return self.jwt_secret


# ============================================================================
# Factory Functions
# ============================================================================

def create_dapr_secrets_service(
    secret_store_name: str = "secretstore"
) -> DaprSecretsService:
    """
    Factory function to create DaprSecretsService instance.

    Args:
        secret_store_name: Dapr secret store component name

    Returns:
        DaprSecretsService: Configured instance
    """
    return DaprSecretsService(secret_store_name=secret_store_name)


def create_secret_config(
    secret_store_name: str = "secretstore"
) -> SecretConfig:
    """
    Factory function to create SecretConfig instance.

    Args:
        secret_store_name: Dapr secret store component name

    Returns:
        SecretConfig: Configured instance (secrets not loaded yet)
    """
    return SecretConfig(secret_store_name=secret_store_name)
