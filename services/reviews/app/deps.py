"""
Dependency utilities for Reviews Service.

Provides FastAPI dependency functions for authentication and authorization.
"""

from fastapi import Depends, HTTPException
from app.auth import get_current_user


def get_current_user_dep(user=Depends(get_current_user)):
    """
    FastAPI dependency to ensure the user is authenticated.

    Args:
        user: The currently authenticated user (injected via Depends).

    Raises:
        HTTPException: If no user is authenticated (status code 401).

    Returns:
        dict: The authenticated user object.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
