"""
JWT service for the Authentication System.

This module provides functionality for generating, verifying, and decoding
JWT access and refresh tokens. It supports configurable expiration times,
secure token encoding, validation, and error handling via FastAPI HTTP
exceptions.

Features:
- Access token creation with configurable expiration.
- Refresh token creation using JWT with extended TTL.
- Validation of access and refresh tokens.
- Clear exception handling for invalid or expired tokens.
"""

import os
import datetime
from typing import Optional

import jwt
from fastapi import HTTPException, status


# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


def create_access_token(user_id: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Create a signed JWT access token for the given user.

    Args:
        user_id (str): The user identifier to embed in the token.
        expires_delta (Optional[datetime.timedelta]):
            Optional custom expiration interval. If not provided,
            the default ACCESS_TOKEN_EXPIRE_MINUTES value is used.

    Returns:
        str: Encoded JWT access token.

    Notes:
        The payload includes:
            - "sub": The user identifier.
            - "exp": Expiration timestamp.
    """
    expire = datetime.datetime.utcnow() + (
        expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> str:
    """
    Validate a JWT access token and extract the user ID.

    Args:
        token (str): The JWT token string to validate.

    Returns:
        str: The user ID retrieved from the token payload.

    Raises:
        HTTPException:
            - 401 Unauthorized if the token is expired.
            - 401 Unauthorized if the token is invalid or the payload is malformed.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload invalid"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_refresh_token() -> str:
    """
    Generate a long-lived JWT refresh token.

    Returns:
        str: A refresh token encoded as a JWT.

    Notes:
        This function uses the same signing key as the access token but sets
        a much longer expiration period.
    """
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_refresh_token(token: str) -> bool:
    """
    Validate a refresh token and ensure it has not expired.

    Args:
        token (str): The refresh token string to validate.

    Returns:
        bool: True if the token is valid.

    Raises:
        HTTPException:
            - 401 Unauthorized if the refresh token is expired.
            - 401 Unauthorized if the token is malformed or invalid.
    """
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
