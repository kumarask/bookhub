"""
User service: business logic for managing users.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.security.hashing import hash_password
from app.schemas.user import UserCreate, UserUpdate
from datetime import datetime


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user."""
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
    """Update existing user profile."""
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
    """Fetch user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Fetch user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch user by email."""
    return db.query(User).filter(User.email == email).first()
