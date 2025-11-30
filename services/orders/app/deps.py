"""
Dependency module for user authentication in FastAPI routes.

Provides a dependency function to ensure that a request has a valid
authenticated user. Raises HTTP 401 Unauthorized if no user is found.
"""

from fastapi import Depends, HTTPException
from app.auth import get_current_user


def get_current_user_dep(user=Depends(get_current_user)):
    """
    FastAPI dependency to retrieve the current authenticated user.

    This function wraps `get_current_user` and enforces authentication.
    If the user is not authenticated, it raises an HTTPException with
    status code 401 (Unauthorized).

    Args:
        user: Injected by FastAPI using Depends(get_current_user)

    Raises:
        HTTPException: If user is None, with status code 401

    Returns:
        dict: Authenticated user information
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
