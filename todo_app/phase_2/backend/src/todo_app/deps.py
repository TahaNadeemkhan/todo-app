"""
Dependency injection utilities for FastAPI routes.
"""

from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, Path, status

from todo_app.config import get_settings

settings = get_settings()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """
    Extract and verify JWT token, return user_id.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        User ID extracted from token's 'sub' claim

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_user_access(
    user_id: Annotated[str, Path(description="User ID from URL path")],
    current_user: Annotated[str, Depends(get_current_user)],
) -> str:
    """
    Validate that the authenticated user matches the user_id in the path.

    Args:
        user_id: User ID from URL path
        current_user: User ID from JWT token

    Returns:
        The validated user_id

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this user",
        )
    return user_id


# Type alias for dependency injection
CurrentUser = Annotated[str, Depends(get_current_user)]
ValidatedUserId = Annotated[str, Depends(validate_user_access)]
