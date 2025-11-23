"""
Authentication service: login, registration, refresh tokens.
"""

from sqlalchemy.orm import Session
from app.security.hashing import verify_password
from app.security.jwt import create_access_token
from app.services.user_service import get_user_by_username
from app.services.token_service import create_refresh_token
from app.schemas.auth import LoginRequest


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user credentials."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login(db: Session, login_in: LoginRequest):
    """Login user and generate access & refresh tokens."""
    user = authenticate_user(db, login_in.username, login_in.password)
    if not user or not user.is_active:
        return None
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(db, user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": user
    }
