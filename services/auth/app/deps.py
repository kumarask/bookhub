"""
Dependency utilities for the Auth Service.

This module provides dependency injection helpers for FastAPI routes,
including database sessions, Redis connections, and current user retrieval.
It also provides admin access enforcement for route-level security.
"""

from fastapi import Depends, HTTPException, status
from redis import Redis
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.database import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    """
    Provide a SQLAlchemy database session for FastAPI routes.

    Yields:
        Session: SQLAlchemy database session.

    Notes:
        - The session is closed automatically after the request finishes.
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


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Retrieve the current user based on the provided JWT access token.

    Args:
        token (str): JWT token injected by FastAPI OAuth2 scheme.
        db (Session): SQLAlchemy session dependency.

    Returns:
        User: The authenticated user instance.

    Raises:
        HTTPException:
            - 401 Unauthorized if the token is invalid or expired.
            - 401 Unauthorized if the user does not exist in the database.
    """
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user has admin privileges.

    Args:
        user (User): Current user injected via `get_current_user`.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException: 403 Forbidden if the user is not an admin.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return user
