"""
Dependency module for user authentication in FastAPI routes.

Provides a dependency function to ensure that a request has a valid
authenticated user. Raises HTTP 401 Unauthorized if no user is found.
"""

from fastapi import Depends, HTTPException
from redis import Redis

from app.auth import get_current_user
from app.database import SessionLocal


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


def get_db():
    """
    Provides a database session for dependency injection.

    This function yields a SQLAlchemy session that can be used in FastAPI
    route handlers. The session is automatically closed after use.

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
    r = Redis(host="localhost", port=6379, db=0, decode_responses=True)
    return r
