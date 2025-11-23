"""
SQLAlchemy models for the Reviews Service.

This module defines the ORM models used by the Reviews Service to persist
review data in a relational database. It includes:

- A SQLAlchemy declarative base
- A UUID generator helper for model primary keys
- The `Review` model, representing individual book reviews

These models integrate with the broader service through SQLAlchemy
sessions created in the database utilities module. The `Review` model
is used throughout the service for CRUD operations, analytics queries,
and domain event emission.
"""

import datetime
import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def gen_uuid():
    """
    Generate a new UUID string.

    Returns:
        str: A randomly generated UUID4 string.

    This helper is used as the default primary key value generator
    for the Review model.
    """
    return str(uuid.uuid4())


class Review(Base):
    """
    SQLAlchemy model representing a book review.

    The `Review` model stores user-submitted ratings and optional textual
    comments associated with a particular book. This model is used
    across the service for creating, retrieving, updating, and deleting
    reviews, as well as generating aggregate statistics.

    Attributes:
        id (str): Primary key UUID identifying the review.
        book_id (str): UUID of the book being reviewed.
        user_id (str): UUID of the user who submitted the review.
        rating (int): Numerical rating (typically 1–5).
        title (str): Optional short title or summary for the review.
        comment (str): Optional detailed text comment.
        created_at (datetime): Timestamp of review creation.
        updated_at (datetime): Timestamp of last update.
    """

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    book_id = Column(UUID(as_uuid=False), nullable=False)
    user_id = Column(UUID(as_uuid=False), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
