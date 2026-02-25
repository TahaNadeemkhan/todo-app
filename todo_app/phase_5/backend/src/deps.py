"""
Dependency injection utilities for FastAPI routes.
"""
from typing import Annotated
import json

import jwt
from fastapi import Depends, Header, HTTPException, Path, status
from sqlmodel import Session

from src.config.settings import get_settings
from src.db import sync_engine as engine
from src.models.jwks import Jwks

settings = get_settings()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """
    Extract and verify JWT token, return user_id.
    Supports both HS256 (Shared Secret) and EdDSA/RS256 (JWKS from DB).
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
        # Inspect Header to determine verification method
        header = jwt.get_unverified_header(token)

        alg = header.get("alg")
        kid = header.get("kid")

        if alg == "HS256":
            # Use Shared Secret
            payload = jwt.decode(
                token,
                settings.better_auth_secret,
                algorithms=["HS256"],
                audience="todo-app-api",
            )
        elif kid:
            # Use Public Key from DB (JWKS)
            with Session(engine) as session:
                jwk_record = session.get(Jwks, kid)
                if not jwk_record:
                    print(f"DEBUG: Key ID {kid} not found in DB")
                    raise jwt.InvalidTokenError("Key ID not found")

                # Parse JWK
                jwk_data = json.loads(jwk_record.public_key)

                # Construct PyJWK
                key = jwt.PyJWK(jwk_data)

                payload = jwt.decode(
                    token,
                    key.key,
                    algorithms=[alg],
                    audience="todo-app-api", # Verify audience matches frontend config
                )
        else:
             raise jwt.InvalidTokenError(f"Unsupported algorithm: {alg}")

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
        print(f"DEBUG: JWT Invalid: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"DEBUG: Unexpected Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_user_access(
    user_id: Annotated[str, Path(description="User ID from URL path")],
    current_user: Annotated[str, Depends(get_current_user)],
) -> str:
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this user",
        )
    return user_id


# Type alias for dependency injection
CurrentUser = Annotated[str, Depends(get_current_user)]
ValidatedUserId = Annotated[str, Depends(validate_user_access)]