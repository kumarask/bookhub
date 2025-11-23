"""
Dependency utilities for the reviews service.

This module defines common FastAPI dependency helpers used throughout the
reviews service, including:

- Database session lifecycle management
- Redis client access
- Authentication and authorization stubs for user/admin checks

These helpers are intended to be injected into FastAPI routes using
`Depends(...)` and allow the rest of the application to interact with
shared resources such as the database and Redis.

Environment Variables:
    REDIS_URL (str): Optional. A Redis connection URL. Defaults to
        "redis://redis:6379/0" if not provided.

All public functions include concise docstrings describing their
purpose, arguments, and behavior.
"""

import os

import redis
from fastapi import HTTPException
from starlette.requests import Request

from .db import SessionLocal


def get_db():
    """
    Provide a database session for a request.

    Yields:
        Session: A SQLAlchemy session bound to the application's database.

    Ensures the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """
    Return a Redis client instance.

    Uses the `REDIS_URL` environment variable if set, otherwise defaults
    to "redis://redis:6379/0".

    Returns:
        redis.Redis: A Redis client connected to the configured server.
    """
    url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    return redis.from_url(url)


def require_admin(request: Request):
    """
    Placeholder dependency that enforces admin access.

    Args:
        request (Request): The incoming HTTP request.

    Raises:
        HTTPException: Always raises 403, as admin checks are not yet implemented.
    """
    raise HTTPException(
        status_code=403, detail="Admin check not implemented in scaffold"
    )


def get_current_user(request: Request):
    """
    Placeholder dependency returning the current user.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        None: User authentication is not implemented in this scaffold.
    """
    return None
