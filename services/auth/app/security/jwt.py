"""
Utility functions for creating and decoding JWT tokens.

This module provides helper functions for generating JWT access tokens
used for authentication and authorization, as well as securely decoding
and validating incoming tokens.
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token for the given subject.

    Args:
        subject (str): The identifier (typically user ID or username) to include in the token.
        expires_delta (Optional[timedelta]): Custom expiration duration. If not provided,
            the default expiration time from configuration is used.

    Returns:
        str: The encoded JWT access token.

    Notes:
        The token includes:
        - "sub": the subject identifier
        - "exp": expiration timestamp (UTC)
    """
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token (str): The JWT token string to decode.

    Returns:
        dict: The decoded payload if the token is valid.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token signature or structure is invalid.
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
