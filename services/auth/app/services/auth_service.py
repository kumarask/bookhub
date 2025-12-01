"""
Authentication service functions for handling user login, credential validation,
and token generation.

This module provides utilities to authenticate users, verify credentials,
and generate JWT access tokens along with persistent refresh tokens.
It integrates with the user service, hashing utilities, and token management
to support secure authentication workflows.
"""

import datetime
from sqlalchemy.orm import Session
from app.security.hashing import verify_password
from app.security.jwt import create_access_token
from app.services.user_service import get_user_by_username
from app.services.token_service import create_refresh_token
from app.schemas.auth import LoginSchema
from app.models.refresh_token import RefreshToken


def authenticate_user(db: Session, username: str, password: str):
    """
    Validate a user's login credentials.

    Args:
        db (Session): SQLAlchemy database session.
        username (str): The username provided by the user.
        password (str): The plain-text password provided by the user.

    Returns:
        User | None: The user object if authentication succeeds,
                     otherwise None.

    Notes:
        - Fetches the user by username.
        - Verifies the provided password using secure hashing.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login(db: Session, login_in: LoginSchema):
    """
    Authenticate a user and generate authentication tokens.

    Args:
        db (Session): SQLAlchemy database session.
        login_in (LoginRequest): Login request containing username and password.

    Returns:
        dict | None: A dictionary containing:
            - access_token (str): Newly issued JWT access token.
            - refresh_token (str): Persistent refresh token.
            - token_type (str): Type of token ("bearer").
            - expires_in (int): Access token expiration time in seconds.
            - user (User): Authenticated user object.
          Returns None if authentication fails or the user is inactive.

    Notes:
        - First validates the user's credentials.
        - Only active users can log in.
        - Utilizes token services to create both access and refresh tokens.
    """
    user = authenticate_user(db, login_in.username, login_in.password)
    if not user or not user.is_active:
        return None

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(user.id, db)

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
    )

    # db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": user,
    }
