"""
SQLAlchemy models for the Auth Service.

This module defines the database models used for user authentication
and account management. It includes the base declarative model, a UUID
generator helper, and the User model that stores core user account
details and metadata.
"""

import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def gen_uuid():
    """
    Generate a new UUID string.

    Returns:
        str: A randomly generated UUID v4 string.
    """
    return str(uuid.uuid4())


class User(Base):
    """
    Represents an application user within the authentication system.

    This model stores essential user account information including login
    credentials, profile details, and account status. It is used throughout the
    authentication service for user creation, verification, and permission checks.

    Attributes:
        id (UUID): Primary key, unique identifier for the user.
        email (str): User's email address, must be unique.
        username (str): Unique username chosen by the user.
        hashed_password (str): Securely hashed password for authentication.
        full_name (str | None): Optional full name of the user.
        is_active (bool): Indicates if the user account is active.
        is_admin (bool): Indicates administrative privileges.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp of the last user record update.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
