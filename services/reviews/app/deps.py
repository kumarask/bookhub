"""
Dependency utilities for Reviews Service.

Provides FastAPI dependency functions for authentication and authorization.
"""

from fastapi import Depends, HTTPException
from redis import Redis

from app.auth import get_current_user
from app.database import SessionLocal


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


def get_db():
    """
    Provide a SQLAlchemy database session for dependency injection.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Redis:
    """
    Provide a Redis client for FastAPI routes.

    Returns:
        Redis: Redis client instance connected to localhost:6379, DB 0.

    Notes:
        - `decode_responses=True` ensures strings are returned instead of bytes.
    """
    r = Redis(host="redis", port=6379, db=0, decode_responses=True)
    return r
