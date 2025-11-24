"""
User service module containing business logic for managing user accounts.

This module provides high-level operations such as creating users,
updating profile information, and retrieving users by various identifiers.
It acts as an abstraction layer between database models and API routes,
ensuring consistent handling of user-related data and operations.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.security.hashing import hash_password
from app.schemas.user import UserCreate, UserUpdate
from datetime import datetime


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user and store it in the database.

    Args:
        db (Session): SQLAlchemy database session.
        user_in (UserCreate): Input schema containing user registration data.

    Returns:
        User: The newly created user instance.

    Notes:
        - Password is securely hashed before saving.
        - The created user is initialized as active and non-admin.
        - Both created_at and updated_at timestamps are set to now.
    """
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, updates: UserUpdate) -> User:
    """
    Update an existing user's profile fields.

    Args:
        db (Session): SQLAlchemy database session.
        user (User): The user instance to update.
        updates (UserUpdate): Schema containing updated user fields.

    Returns:
        User: The updated user instance.

    Notes:
        - Only non-null fields in the update schema are applied.
        - Updates the `updated_at` timestamp automatically.
    """
    if updates.email:
        user.email = updates.email
    if updates.full_name:
        user.full_name = updates.full_name

    user.updated_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """
    Retrieve a user by their unique ID.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (str): The user's ID.

    Returns:
        User | None: The user instance if found, otherwise None.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Retrieve a user by their username.

    Args:
        db (Session): SQLAlchemy database session.
        username (str): The username to search for.

    Returns:
        User | None: The matching user instance, or None if not found.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by their email address.

    Args:
        db (Session): SQLAlchemy database session.
        email (str): The user's email address.

    Returns:
        User | None: The matching user instance, or None if no match exists.
    """
    return db.query(User).filter(User.email == email).first()
