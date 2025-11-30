"""
SQLAlchemy models for managing book records within the application.

This module defines the `Book` ORM model, which represents individual
books in the system, including metadata such as title, author, ISBN,
pricing, inventory counts, publication details, and category associations.

The model integrates with PostgreSQL using SQLAlchemy's UUID type and
automatically manages creation and update timestamps.
"""

import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    DECIMAL,
    Integer,
    Date,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class Book(Base):
    """
    Represents a book in the system’s inventory.

    This SQLAlchemy model defines all metadata associated with a book,
    including bibliographic details, pricing, stock information, and
    relations to other entities such as categories.

    Attributes:
        id (UUID): Unique identifier for the book, generated automatically.
        title (str): Title of the book. Required.
        author (str): Name of the book's author. Required.
        isbn (str): Unique ISBN number assigned to the book. Required and unique.
        description (str): Optional detailed description or summary of the book.
        price (Decimal): Price of the book with precision up to two decimal places. Required.
        stock_quantity (int): Number of available copies in inventory. Defaults to 0.

        category_id (UUID): Optional foreign key linking the book to a category.
        category (Category): Relationship object representing the associated category.

        publisher (str): Name of the book's publisher.
        published_date (date): Date the book was officially published.

        created_at (datetime): Timestamp indicating when the record was created.
        updated_at (datetime): Timestamp automatically updated when the record changes.
    """

    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)

    # Link to category table
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")

    publisher = Column(String)
    published_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
