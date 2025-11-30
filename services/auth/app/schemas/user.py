"""
Pydantic schemas for user-related operations, including user creation,
retrieval, and update actions.

These models provide input validation, enforce field constraints,
and define consistent response structures for user management endpoints.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    Schema used when creating a new user account.

    Fields:
        email (EmailStr): The user's email address.
        username (str): The chosen username for the account.
        password (str): The user's raw password, which will be hashed.
        full_name (Optional[str]): The user's full name (optional).
    """

    email: EmailStr
    username: str
    password: str
    full_name: Optional[str]


class UserResponse(BaseModel):
    """
    Schema returned when retrieving user information.

    Fields:
        id (str): Unique identifier of the user.
        email (EmailStr): The user's email address.
        username (str): The user's username.
        full_name (Optional[str]): The user's full name.
        is_active (bool): Indicates whether the user account is active.
        is_admin (bool): Whether the user has administrative privileges.
        created_at (datetime): Timestamp when the user was created.

    Notes:
        orm_mode = True allows compatibility with ORM objects such as SQLAlchemy models.
    """

    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    """
    Schema used for updating user profile information.

    Fields:
        email (Optional[EmailStr]): The updated email address (optional).
        full_name (Optional[str]): The updated full name (optional).
    """

    email: Optional[EmailStr]
    full_name: Optional[str]
