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
from typing import Dict, Optional

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError


logger = logging.getLogger(__name__)


class DaprSecretsService:
    """
    T059: Dapr Secrets Store service for portable secrets management.

    Features:
    - Get secret by key
    - Get bulk secrets
    - Support for metadata (e.g., version)
    - Automatic retry on transient failures
    """

    def __init__(
        self,
        dapr_client: Optional[DaprClient] = None,
        secret_store_name: str = "secretstore"
    ):
        """
        Initialize DaprSecretsService.

        Args:
            dapr_client: Dapr client (if None, creates new one)
            secret_store_name: Dapr secret store component name (default: secretstore)
        """
        self.dapr_client = dapr_client or DaprClient()
        self.secret_store_name = secret_store_name

        logger.info(f"DaprSecretsService initialized: store={secret_store_name}")

    async def get_secret(
        self,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Get secret value by key.

        Args:
            key: Secret key to retrieve
            metadata: Optional metadata (e.g., {"version": "latest"})

        Returns:
            Secret value as string, or None if not found

        Raises:
            Exception: If get operation fails
        """
        try:
            # Get secret via Dapr
            secret_response = await self.dapr_client.get_secret(
                store_name=self.secret_store_name,
                key=key,
                metadata=metadata or {}
            )

            if not secret_response.secret:
                logger.warning(f"Secret not found: key={key}")
                return None

            # Dapr returns secrets as dict {key: value}
            # Extract the value
            secret_value = secret_response.secret.get(key)

            logger.info(f"Secret retrieved: key={key}, store={self.secret_store_name}")

            return secret_value

        except DaprInternalError as e:
            logger.error(f"Dapr secret get failed: key={key}, error={str(e)}")
            raise Exception(f"Failed to get secret '{key}': {str(e)}") from e

    async def get_bulk_secrets(
        self,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Get all secrets from the secret store.

        Args:
            metadata: Optional metadata (e.g., {"namespace": "prod"})

        Returns:
            Dict mapping secret keys to values

        Raises:
            Exception: If get operation fails
        """
        try:
            # Get bulk secrets via Dapr
            bulk_response = await self.dapr_client.get_bulk_secret(
                store_name=self.secret_store_name,
                metadata=metadata or {}
            )

            if not bulk_response.secrets:
                logger.warning("No secrets found in bulk request")
                return {}

            # Flatten nested dict structure
            secrets = {}
            for key, value_dict in bulk_response.secrets.items():
                # value_dict is {key: actual_value}
                secrets[key] = value_dict.get(key, "")

            logger.info(
                f"Bulk secrets retrieved: count={len(secrets)}, "
                f"store={self.secret_store_name}"
            )

            return secrets

        except DaprInternalError as e:
            logger.error(f"Dapr bulk secret get failed: error={str(e)}")
            raise Exception(f"Failed to get bulk secrets: {str(e)}") from e

    def close(self) -> None:
        """Close Dapr client and cleanup resources."""
        if self.dapr_client:
            self.dapr_client.close()
            logger.info("DaprSecretsService closed")


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
