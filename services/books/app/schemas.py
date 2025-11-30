"""
Pydantic schemas for books and categories.

This module defines data validation and serialization models used in
the Books Service API. It includes schemas for creating, updating,
and returning book and category data, as well as specialized outputs
such as lists, details, and stock updates.

Schemas:
    - BookBase: Base schema for common book fields.
    - BookCreate: Schema for creating a new book.
    - BookUpdate: Schema for updating existing book fields.
    - BookOut: Schema for returning book data in responses.
    - BookDetailOut: Schema for detailed book view, including ratings and reviews.
    - BookListOut: Schema for paginated book lists.
    - BookStockUpdate: Schema for changing book stock quantities.
    - BookStockOut: Schema for returning updated stock info.
    - CategoryOut: Schema for returning category details with optional book count.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class BookBase(BaseModel):
    """
    Base schema for book-related data.

    Includes all common fields shared between creation and output schemas.
    """

    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    price: float
    stock_quantity: Optional[int] = 0
    category: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None


class BookCreate(BookBase):
    """
    Schema used when creating a new book.

    Inherits all fields from BookBase and optionally allows setting created_at.
    """

    created_at: Optional[date] = None


class BookUpdate(BaseModel):
    """
    Schema for updating an existing book.

    Only the fields that may change are included and are optional.
    """

    price: Optional[float]
    stock_quantity: Optional[int]
    description: Optional[str]


class BookOut(BaseModel):
    """
    Schema for returning book information in API responses.

    Includes the book's unique ID and optional category info.
    """

    id: UUID
    title: str
    author: str
    isbn: str
    price: float
    stock_quantity: int
    category: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    """
    Schema for returning category information with optional book count.

    Includes unique category ID, name, description, and the number of books
    in this category.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    book_count: Optional[int] = 0

    class Config:
        from_attributes = True


class BookListOut(BaseModel):
    """
    Schema for paginated book list responses.

    Includes the list of books, total count, current page, page limit,
    and total number of pages.
    """

    items: list[BookOut]
    total: int
    page: int
    limit: int
    pages: int


class BookDetailOut(BaseModel):
    """
    Schema for detailed book view including ratings and reviews.

    Provides all book attributes, category info, publisher, and optional
    statistics like average rating and review count.
    """

    id: UUID
    title: str
    author: str
    isbn: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category: Optional[str]
    publisher: Optional[str]
    published_date: Optional[date]
    average_rating: Optional[float] = 0.0
    review_count: Optional[int] = 0

    class Config:
        from_attributes = True


class BookStockUpdate(BaseModel):
    """
    Schema for updating book stock quantities.

    Contains the quantity change to apply (positive or negative).
    """

    quantity_change: int


class BookStockOut(BaseModel):
    """
    Schema for returning updated book stock information.

    Includes the book ID, current stock quantity, and the timestamp of the update.
    """

    id: UUID
    stock_quantity: int
    updated_at: datetime

    class Config:
        from_attributes = True
