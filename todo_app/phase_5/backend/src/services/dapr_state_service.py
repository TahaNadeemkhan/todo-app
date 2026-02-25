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
from typing import Any, Dict, Optional, List
import json

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError
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
    T056: Dapr State Store service for portable state management.

    Features:
    - Save/get state operations (T057)
    - Support for ETags (optimistic concurrency)
    - Bulk operations (save_bulk, get_bulk, delete_bulk)
    - State metadata for TTL and custom tags
    """

    def __init__(
        self,
        dapr_client: Optional[DaprClient] = None,
        store_name: str = "statestore"
    ):
        """
        Initialize DaprStateService.

        Args:
            dapr_client: Dapr client (if None, creates new one)
            store_name: Dapr state store component name (default: statestore)
        """
        self.dapr_client = dapr_client or DaprClient()
        self.store_name = store_name

        logger.info(f"DaprStateService initialized: store_name={store_name}")

    async def save_state(
        self,
        key: str,
        value: Any,
        etag: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        T057: Save state to Dapr State Store.

        Args:
            key: State key (unique identifier)
            value: State value (will be JSON-serialized)
            etag: Optional ETag for optimistic concurrency
            metadata: Optional metadata (e.g., TTL: {"ttlInSeconds": "3600"})

        Raises:
            Exception: If save operation fails
        """
        try:
            # Serialize value to JSON string
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif isinstance(value, BaseModel):
                serialized_value = value.model_dump_json()
            else:
                serialized_value = str(value)

            # Save state via Dapr
            await self.dapr_client.save_state(
                store_name=self.store_name,
                key=key,
                value=serialized_value,
                etag=etag,
                state_metadata=metadata or {}
            )

            logger.info(
                f"State saved: key={key}, store={self.store_name}, "
                f"has_etag={etag is not None}, has_metadata={metadata is not None}"
            )

        except DaprInternalError as e:
            logger.error(f"Dapr state save failed: key={key}, error={str(e)}")
            raise Exception(f"Failed to save state: {str(e)}") from e

    async def get_state(
        self,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """
        T057: Get state from Dapr State Store.

        Args:
            key: State key to retrieve
            default: Default value if key not found

        Returns:
            State value (deserialized from JSON) or default

        Raises:
            Exception: If get operation fails
        """
        try:
            # Get state via Dapr
            state_response = await self.dapr_client.get_state(
                store_name=self.store_name,
                key=key
            )

            if not state_response.data:
                logger.debug(f"State not found: key={key}, returning default")
                return default

            # Deserialize JSON
            value = json.loads(state_response.data)

            logger.info(f"State retrieved: key={key}, store={self.store_name}")

            return value

        except DaprInternalError as e:
            logger.error(f"Dapr state get failed: key={key}, error={str(e)}")
            raise Exception(f"Failed to get state: {str(e)}") from e
        except json.JSONDecodeError:
            # If not JSON, return raw string
            return state_response.data

    async def delete_state(
        self,
        key: str,
        etag: Optional[str] = None
    ) -> None:
        """
        Delete state from Dapr State Store.

        Args:
            key: State key to delete
            etag: Optional ETag for optimistic concurrency

        Raises:
            Exception: If delete operation fails
        """
        try:
            await self.dapr_client.delete_state(
                store_name=self.store_name,
                key=key,
                etag=etag
            )

            logger.info(f"State deleted: key={key}, store={self.store_name}")

        except DaprInternalError as e:
            logger.error(f"Dapr state delete failed: key={key}, error={str(e)}")
            raise Exception(f"Failed to delete state: {str(e)}") from e

    async def save_bulk(
        self,
        items: List[StateItem]
    ) -> None:
        """
        Save multiple state items in a single transaction.

        Args:
            items: List of StateItem objects to save

        Raises:
            Exception: If bulk save operation fails
        """
        try:
            states = []
            for item in items:
                # Serialize value
                if isinstance(item.value, (dict, list)):
                    serialized_value = json.dumps(item.value)
                elif isinstance(item.value, BaseModel):
                    serialized_value = item.value.model_dump_json()
                else:
                    serialized_value = str(item.value)

                states.append({
                    "key": item.key,
                    "value": serialized_value,
                    "etag": item.etag,
                    "metadata": item.metadata or {}
                })

            # Bulk save via Dapr
            await self.dapr_client.save_bulk_state(
                store_name=self.store_name,
                states=states
            )

            logger.info(
                f"Bulk state saved: count={len(items)}, store={self.store_name}"
            )

        except DaprInternalError as e:
            logger.error(f"Dapr bulk state save failed: error={str(e)}")
            raise Exception(f"Failed to save bulk state: {str(e)}") from e

    async def get_bulk(
        self,
        keys: List[str]
    ) -> Dict[str, Any]:
        """
        Get multiple state items in a single request.

        Args:
            keys: List of state keys to retrieve

        Returns:
            Dict mapping keys to values (keys not found are omitted)

        Raises:
            Exception: If bulk get operation fails
        """
        try:
            # Bulk get via Dapr
            bulk_response = await self.dapr_client.get_bulk_state(
                store_name=self.store_name,
                keys=keys
            )

            result = {}
            for item in bulk_response.items:
                if item.data:
                    try:
                        result[item.key] = json.loads(item.data)
                    except json.JSONDecodeError:
                        result[item.key] = item.data

            logger.info(
                f"Bulk state retrieved: requested={len(keys)}, "
                f"found={len(result)}, store={self.store_name}"
            )

            return result

        except DaprInternalError as e:
            logger.error(f"Dapr bulk state get failed: error={str(e)}")
            raise Exception(f"Failed to get bulk state: {str(e)}") from e

    async def delete_bulk(
        self,
        keys: List[str]
    ) -> None:
        """
        Delete multiple state items.

        Args:
            keys: List of state keys to delete

        Raises:
            Exception: If bulk delete operation fails
        """
        try:
            states = [{"key": key} for key in keys]

            await self.dapr_client.delete_bulk_state(
                store_name=self.store_name,
                states=states
            )

            logger.info(
                f"Bulk state deleted: count={len(keys)}, store={self.store_name}"
            )

        except DaprInternalError as e:
            logger.error(f"Dapr bulk state delete failed: error={str(e)}")
            raise Exception(f"Failed to delete bulk state: {str(e)}") from e

    def close(self) -> None:
        """Close Dapr client and cleanup resources."""
        if self.dapr_client:
            self.dapr_client.close()
            logger.info("DaprStateService closed")


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
