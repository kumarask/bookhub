"""
Database models for the Reviews Service.

Defines the ORM model for storing book reviews in the database.
Each review is associated with a specific book and user, and contains
a rating, optional title and comment, along with timestamps for creation
and updates.
"""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

import uuid
from app.database import Base


class Review(Base):
    """
    SQLAlchemy model representing a book review.

    Attributes:
        id (UUID): Primary key for the review.
        book_id (UUID): ID of the book being reviewed.
        user_id (UUID): ID of the user who created the review.
        rating (int): Rating given by the user (typically 1-5).
        title (str, optional): Title of the review.
        comment (str, optional): Text content of the review.
        created_at (datetime): Timestamp when the review was created.
        updated_at (datetime): Timestamp when the review was last updated.

    Constraints:
        - Unique constraint on (book_id, user_id) to ensure a user can
          only review a book once.
    """

    __tablename__ = "reviews"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(PG_UUID(as_uuid=True), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    __table_args__ = (
        # Enforce unique review per user per book
        {"sqlite_autoincrement": True},
    )
