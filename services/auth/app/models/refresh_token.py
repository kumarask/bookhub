"""
SQLAlchemy model for storing refresh tokens used in the authentication system.

This module defines the RefreshToken model, which associates long-lived
refresh tokens with users. These tokens allow clients to request new
access tokens without requiring the user to re-authenticate.
"""

import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.user import Base


class RefreshToken(Base):
    """
    Represents a refresh token issued to a user for authentication.

    This model stores long-lived refresh tokens that allow clients to obtain new
    access tokens after the previous ones expire. Each refresh token is tied to
    a specific user and has an expiration timestamp.

    Attributes:
        id (UUID): Unique identifier for the refresh token.
        user_id (UUID): Foreign key referencing the associated user.
        token (str): The refresh token string, unique per entry.
        expires_at (datetime): Timestamp when the refresh token becomes invalid.
        created_at (datetime): Timestamp when the token was created.
        user (User): Relationship mapping to the associated User model.
    """

    __tablename__ = "refresh_tokens"

    id = Column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
