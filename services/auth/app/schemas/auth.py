"""
This module defines Pydantic data models used for request and response
validation in the authentication and user management system.

It includes:
- Request schemas for user registration, login, token refresh, logout,
  and profile update operations.
- Response schemas for user details, authentication tokens, messages,
  and error handling.

The models ensure type safety, enforce field validation rules, and provide
a structured interface between API endpoints and clients.
"""


from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

# Request Schemas

class RegisterSchema(BaseModel):
    """
    Schema for user registration requests.

    Fields:
        email (EmailStr): The user's email address.
        username (str): A username between 3 and 50 characters.
        password (str): A password with a minimum length of 6 characters.
        full_name (Optional[str]): The user's full name (optional).
    """
    email: EmailStr
    username: constr(min_length=3, max_length=50) # type: ignore
    password: constr(min_length=6) # type: ignore
    full_name: Optional[str]


class LoginSchema(BaseModel):
    """
    Schema for user login requests.

    Fields:
        username (str): The username or email used for login.
        password (str): The user's password.
    """
    username: str
    password: str


class RefreshTokenSchema(BaseModel):
    """
    Schema for requesting a new access token using a refresh token.

    Fields:
        refresh_token (str): The refresh token issued during login.
    """
    refresh_token: str


class TokenSchema(BaseModel):
    """
    Schema returned after successful authentication, containing token data.

    Fields:
        access_token (str): The JWT access token.
        refresh_token (str): A token used to generate new access tokens.
        token_type (str): Token type, default is 'bearer'.
        expires_in (int): Expiration time of the access token in seconds.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserSchema(BaseModel):
    """
    Full schema representing a user in the system.

    Fields:
        id (str): Unique identifier for the user.
        email (EmailStr): The user's email address.
        username (str): The user's username.
        full_name (Optional[str]): The user's full name.
        is_active (bool): Indicates if the account is active.
        is_admin (bool): Whether the user has admin privileges.
        created_at (datetime): Timestamp of user creation.
        updated_at (Optional[datetime]): Timestamp of last profile update.
    """
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime]


class UserResponseSchema(BaseModel):
    """
    Schema returned to clients when retrieving basic user info.

    Fields:
        id (str): The user's unique identifier.
        email (EmailStr): The user's email address.
        username (str): The user's username.
        full_name (Optional[str]): The user's full name.
        is_active (bool): Indicates if the user is active.
        created_at (datetime): When the user was created.
    """
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime


class ErrorResponseSchema(BaseModel):
    """
    Schema representing an error response.

    Fields:
        detail (str): Description of the error encountered.
    """
    detail: str


class UserProfileSchema(BaseModel):
    """
    Schema representing a user's profile details.

    Fields:
        id (str): Unique identifier for the user.
        email (str): Email address of the user.
        username (str): Username of the user.
        full_name (str): Full name of the user.
        is_active (bool): Whether the user is active.
        is_admin (bool): Whether the user has admin privileges.
        created_at (datetime): Account creation timestamp.
    """
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime


class LogoutRequestSchema(BaseModel):
    """
    Schema used to request logout and refresh token invalidation.

    Fields:
        refresh_token (str): The refresh token to revoke.
    """
    refresh_token: str


class MessageResponseSchema(BaseModel):
    """
    Generic message response schema.

    Fields:
        message (str): A human-readable message describing the result.
    """
    message: str


class ProfileUpdateSchema(BaseModel):
    """
    Schema for updating a user's profile information.

    Fields:
        full_name (str): The user's updated full name.
        email (EmailStr): The user's updated email address.
    """
    full_name: str
    email: EmailStr


class UpdatedUserResponseSchema(BaseModel):
    """
    Schema returned after successfully updating a user's profile.

    Fields:
        id (str): The user's unique identifier.
        email (EmailStr): The updated email address.
        username (str): The user's username.
        full_name (str): The updated full name.
        updated_at (datetime): Timestamp of the update.
    """

    id: str
    email: EmailStr
    username: str
    full_name: str
    updated_at: datetime

    class Config:
        from_attributes = True
