"""
JWT Service for Auth Service.

This module handles JWT access token generation, verification, and decoding,
as well as refresh token creation and validation.

All public functions include concise docstrings describing their arguments,
return values, and raised exceptions where applicable.
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
    Create a JWT access token.

    Args:
        user_id (str): The user ID to encode in the token.
        expires_delta (Optional[datetime.timedelta]): Custom expiration time.

    Returns:
        str: Encoded JWT access token.
    """
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> str:
    """
    Verify a JWT access token and return the user ID.

    Args:
        token (str): JWT token string.

    Returns:
        str: User ID extracted from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload invalid")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def create_refresh_token() -> str:
    """
    Generate a random JWT-like refresh token.

    Returns:
        str: Random refresh token string.
    """
    # For simplicity, using a JWT with long expiry
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_refresh_token(token: str) -> bool:
    """
    Verify a refresh token.

    Args:
        token (str): Refresh token string.

    Returns:
        bool: True if valid, False otherwise.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
