"""
Dependency utilities for the Auth Service.

This module provides dependency injection helpers for FastAPI routes,
including database sessions, Redis connections, and current user retrieval.
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
    Dependency to provide a SQLAlchemy database session.

    Yields:
        Session: SQLAlchemy session.

    Ensures the session is closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis() -> Redis:
    """
    Dependency to provide a Redis client.

    Returns:
        Redis: Redis client instance.
    """
    r = Redis(host="localhost", port=6379, db=0, decode_responses=True)
    return r


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decode access token and return the user object.
    Raise 401 if token is invalid/expired.
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
    Dependency to require the current user to be an admin.

    Args:
        user (User): Current user (injected via get_current_user).

    Returns:
        User: Admin user.

    Raises:
        HTTPException: If user is not an admin.
    """
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
