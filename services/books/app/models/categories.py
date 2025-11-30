"""
SQLAlchemy model defining book categories used within the application.

This module contains the `Category` ORM model, which represents
classification groups for organizing books. Each category includes
a unique name and an optional description, allowing books to be grouped
and managed more effectively across the system.
"""

import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Category(Base):
    """
    Represents a book category within the system.

    This SQLAlchemy model stores classification data used to organize books.
    Each category includes a unique name and an optional description.

    Attributes:
        id (UUID): Unique identifier for the category, generated automatically.
        name (str): Name of the category. Must be unique and cannot be null.
        description (str): Optional text describing the category or its purpose.
    """

    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
