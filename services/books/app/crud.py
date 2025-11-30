"""
CRUD operations for managing Book records in the database.

This module provides helper functions used for creating, retrieving,
listing, updating, and deleting books. It integrates with SQLAlchemy ORM
and validates relationships such as category existence before creation.

Functions:
    - create_book: Add a new book with category validation and ISBN checks.
    - get_book: Retrieve a book by its ID.
    - list_books: Retrieve a paginated list of books.
    - update_book: Modify an existing book's fields.
    - delete_book: Remove a book from the database.
"""

from sqlalchemy.orm import Session
from app.models import books, categories
from app import schemas


def create_book(db: Session, book: schemas.BookCreate):
    """
    Create a new book record in the database.

    This function ensures the ISBN is unique and validates the category
    (if provided) before inserting the new book.

    Args:
        db (Session): SQLAlchemy database session.
        book (schemas.BookCreate): Pydantic schema containing book details.

    Returns:
        books.Book: The newly created Book ORM object.

    Raises:
        ValueError: If the ISBN already exists or the category is invalid.
    """
    # Check ISBN
    if db.query(books.Book).filter(books.Book.isbn == book.isbn).first():
        raise ValueError("ISBN already exists")

    # Validate category exists
    category_obj = None
    if book.category:
        category_obj = (
            db.query(categories.Category)
            .filter(categories.Category.name == book.category)
            .first()
        )
        if not category_obj:
            raise ValueError("Category does not exist")

    db_book = books.Book(
        **book.dict(exclude={"category"}),
        category_id=category_obj.id if category_obj else None,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book(db: Session, book_id: str):
    """
    Retrieve a single book by its unique ID.

    Args:
        db (Session): SQLAlchemy session.
        book_id (str): UUID of the book.

    Returns:
        books.Book | None: The matching book object, or None if not found.
    """
    return db.query(books.Book).filter(books.Book.id == book_id).first()


def list_books(db: Session, skip: int = 0, limit: int = 20):
    """
    Retrieve a paginated list of books.

    Args:
        db (Session): SQLAlchemy session.
        skip (int): Number of records to skip. Defaults to 0.
        limit (int): Maximum number of records to return. Defaults to 20.

    Returns:
        list[books.Book]: A list of Book objects.
    """
    return db.query(books.Book).offset(skip).limit(limit).all()


def update_book(db: Session, db_book: books.Book, updates: schemas.BookUpdate):
    """
    Update an existing book with the provided fields.

    Only fields explicitly set in the update schema are modified.

    Args:
        db (Session): SQLAlchemy session.
        db_book (books.Book): The existing Book object to update.
        updates (schemas.BookUpdate): Pydantic schema with updated fields.

    Returns:
        books.Book: The updated Book object.
    """
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, db_book: books.Book):
    """
    Delete a book from the database.

    Args:
        db (Session): SQLAlchemy session.
        db_book (books.Book): The Book object to remove.

    Returns:
        None
    """
    db.delete(db_book)
    db.commit()
