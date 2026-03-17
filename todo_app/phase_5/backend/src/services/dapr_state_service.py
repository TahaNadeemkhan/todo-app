"""
T056-T058: DaprStateService - Dapr State Store abstraction

Provides portable state management using Dapr State API.
Abstracts PostgreSQL/Redis/CosmosDB behind a common interface.

Use Cases:
- Conversation history storage (T058)
- Session management
- Cache layer
- Any key-value state that needs portability
"""

import logging
import os
from typing import Any, Dict, Optional, List
import json
import httpx
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class StateItem(BaseModel):
    """Represents a state item with metadata."""
    key: str
    value: Any
    etag: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class DaprStateService:
    """
    T056: Dapr State Store service for portable state management using HTTP API.
    Bypasses Dapr SDK for compatibility with Python 3.13.
    """

    def __init__(
        self,
        dapr_http_port: str = "3500",
        store_name: str = "statestore"
    ):
        """
        Initialize DaprStateService.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
            store_name: Dapr state store component name (default: statestore)
        """
        port = os.getenv("DAPR_HTTP_PORT", dapr_http_port)
        self.dapr_url = f"http://localhost:{port}/v1.0/state/{store_name}"
        self.store_name = store_name

        logger.info(f"DaprStateService (HTTP) initialized: store_name={store_name} at {self.dapr_url}")

    async def save_state(
        self,
        key: str,
        value: Any,
        etag: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        T057: Save state to Dapr State Store using HTTP.
        """
        try:
            # Standard Dapr State item format
            state_data = [{
                "key": key,
                "value": value,
                "etag": etag,
                "metadata": metadata or {}
            }]

            async with httpx.AsyncClient() as client:
                response = await client.post(self.dapr_url, json=state_data, timeout=5.0)
                response.raise_for_status()

            logger.info(f"State saved: key={key}, store={self.store_name}")

        except Exception as e:
            logger.error(f"Dapr state save failed: key={key}, error={str(e)}")
            raise Exception(f"Failed to save state: {str(e)}") from e

    async def get_state(
        self,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """
        T057: Get state from Dapr State Store using HTTP.
        """
        try:
            url = f"{self.dapr_url}/{key}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                
                if response.status_code == 204: # No Content / Not Found
                    return default
                
                response.raise_for_status()
                # Dapr returns raw value for GET /{key}
                try:
                    return response.json()
                except:
                    return response.text

        except Exception as e:
            logger.error(f"Dapr state get failed: key={key}, error={str(e)}")
            return default

    async def delete_state(
        self,
        key: str,
        etag: Optional[str] = None
    ) -> None:
        """
        Delete state from Dapr State Store using HTTP.
        """
        try:
            url = f"{self.dapr_url}/{key}"
            params = {}
            if etag:
                params["etag"] = etag
                
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, params=params, timeout=5.0)
                response.raise_for_status()

            logger.info(f"State deleted: key={key}, store={self.store_name}")

        except Exception as e:
            logger.error(f"Dapr state delete failed: key={key}, error={str(e)}")
            raise Exception(f"Failed to delete state: {str(e)}") from e

    async def save_bulk(
        self,
        items: List[StateItem]
    ) -> None:
        """
        Save multiple state items using HTTP.
        """
        try:
            state_data = []
            for item in items:
                state_data.append({
                    "key": item.key,
                    "value": item.value,
                    "etag": item.etag,
                    "metadata": item.metadata or {}
                })

            async with httpx.AsyncClient() as client:
                response = await client.post(self.dapr_url, json=state_data, timeout=5.0)
                response.raise_for_status()

            logger.info(f"Bulk state saved: count={len(items)}, store={self.store_name}")

        except Exception as e:
            logger.error(f"Dapr bulk state save failed: error={str(e)}")
            raise Exception(f"Failed to save bulk state: {str(e)}") from e

    def close(self) -> None:
        """Cleanup."""
        pass


# ============================================================================
# Factory Function
# ============================================================================

def create_dapr_state_service(
    store_name: str = "statestore"
) -> DaprStateService:
    """
    Factory function to create DaprStateService instance.

    Args:
        store_name: Dapr state store component name

    Returns:
        DaprStateService: Configured instance
    """
    return DaprStateService(store_name=store_name)
