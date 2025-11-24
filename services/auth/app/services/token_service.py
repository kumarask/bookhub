"""
Refresh token service for the authentication system.

This module provides functionality for creating, validating, and blacklisting
refresh tokens that are stored in the database. These tokens allow users to
obtain new access tokens without re-authenticating and support long-lived
sessions.

Features:
- Secure refresh token generation
- Persistent token storage in the database
- Validation and expiration checks
- Blacklisting (revocation) by deletion
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken


def create_refresh_token(user_id: str, db: Session, expires_in: int = 3600*24*7) -> str:
    """
    Create and store a new refresh token for a user.

    Args:
        user_id (str): The ID of the user the refresh token belongs to.
        db (Session): SQLAlchemy database session.
        expires_in (int): Expiration time in seconds (default: 7 days).

    Returns:
        str: The newly created refresh token string.

    Notes:
        - Uses `secrets.token_urlsafe()` to generate a cryptographically secure token.
        - Stores token metadata (user, expiry) in the database.
        - Returns only the token string for client use.
    """
    import secrets

    token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    r = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r.token


def verify_refresh_token(token: str, db: Session) -> bool:
    """
    Verify whether a refresh token exists and is still valid.

    Args:
        token (str): The refresh token string to validate.
        db (Session): SQLAlchemy database session.

    Returns:
        bool: True if the token exists and has not expired, False otherwise.

    Notes:
        - Checks database for presence of the token.
        - Ensures token has not passed its expiration timestamp.
    """
    r = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not r:
        return False
    if r.expires_at < datetime.utcnow():
        return False
    return True


def blacklist_token(token: str, db: Session):
    """
    Invalidate (revoke) a refresh token by removing it from storage.

    Args:
        token (str): The refresh token to invalidate.
        db (Session): SQLAlchemy database session.

    Notes:
        - Deletes the token record from the database.
        - A distributed system may also store revoked tokens in Redis for fast checks.
    """
    r = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if r:
        db.delete(r)
        db.commit()
