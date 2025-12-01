"""
Authentication and authorization utilities for the FastAPI application.

This module provides helpers for validating JWT access tokens and enforcing
role-based access control. It defines:

- `get_current_user`: Extracts and validates a user from a JWT token.
- `admin_required`: Ensures that the authenticated user has admin privileges.

These utilities integrate with FastAPI's dependency injection system
and use OAuth2 Bearer tokens for authentication.
"""

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import (
    JWT_SECRET_KEY as SECRET_KEY,
    JWT_ALGORITHM as ALGORITHM,
    AUTH_SERVICE_URL as AUTH_URL,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_URL}/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode and validate the JWT access token provided by the client.

    Args:
        token (str): JWT access token extracted from the request via OAuth2.

    Returns:
        dict: The decoded JWT payload containing user information.

    Raises:
        HTTPException: If the token is invalid, malformed, or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )


def get_user_info(user_id: str):
    """
    Fetch user information from the authentication service.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        dict: A dictionary containing the user's information as returned
              by the authentication service in JSON format.

    Raises:
        requests.exceptions.RequestException: If there is an issue
              with the HTTP request to the authentication service.
    """
    response = requests.get(
        f"{AUTH_URL}/api/v1/user/{user_id}",
        headers={"Content-Type": "application/json"},
        params={},
    )
    return response.json()


def admin_required(user: dict = Depends(get_current_user)):
    """
    Dependency that ensures the authenticated user has admin privileges.

    Args:
        user (dict): Decoded JWT payload returned by `get_current_user`.

    Returns:
        dict: The authenticated user payload if they have admin access.

    Raises:
        HTTPException: If the authenticated user is not an admin.
    """
    user_data = get_user_info(user.get("sub", ""))
    if not user_data.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user
