"""
CRUD operations for the Reviews Service.

This module provides functions to create, read, update, delete, and list book reviews
from the database. Includes support for pagination, filtering, and sorting.
"""

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate
from datetime import datetime


def create_review(db: Session, review_data: ReviewCreate, user_id: str):
    """
    Create a new review for a book by a specific user.

    Validates that the user hasn't already reviewed the book.

    Args:
        db (Session): SQLAlchemy database session.
        review_data (ReviewCreate): Pydantic schema containing review details.
        user_id (str): UUID of the user creating the review.

    Raises:
        ValueError: If the user has already reviewed the book.

    Returns:
        Review: The newly created Review ORM object.
    """

    existing = (
        db.query(Review)
        .filter(Review.book_id == review_data.book_id, Review.user_id == user_id)
        .first()
    )
    if existing:
        raise ValueError("User already reviewed this book")

    review = Review(
        book_id=review_data.book_id,
        user_id=user_id,
        rating=review_data.rating,
        title=review_data.title,
        comment=review_data.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_review(db: Session, review_id: str):
    """
    Retrieve a review by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        review_id (str): UUID of the review.

    Returns:
        Review | None: The Review object if found, else None.
    """
    return db.query(Review).filter(Review.id == review_id).first()


def update_review(db: Session, review: Review, data: ReviewUpdate):
    """
    Update an existing review with new data.

    Only updates fields provided in the ReviewUpdate schema and sets the updated_at timestamp.

    Args:
        db (Session): SQLAlchemy database session.
        review (Review): The Review ORM object to update.
        data (ReviewUpdate): Pydantic schema with fields to update.

    Returns:
        Review: The updated Review ORM object.
    """
    if data.rating is not None:
        review.rating = data.rating
    if data.title is not None:
        review.title = data.title
    if data.comment is not None:
        review.comment = data.comment
    review.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review: Review):
    """
    Delete a review from the database.

    Args:
        db (Session): SQLAlchemy database session.
        review (Review): The Review ORM object to delete.

    Returns:
        None
    """
    db.delete(review)
    db.commit()


def list_reviews_by_book(
    db: Session,
    book_id: str,
    rating=None,
    page=1,
    limit=20,
    sort_by="created_at",
    sort_order="desc",
):
    """
    List reviews for a specific book with optional rating filter, pagination, and sorting.

    Args:
        db (Session): SQLAlchemy database session.
        book_id (str): UUID of the book.
        rating (int, optional): Filter reviews by this rating (1-5). Defaults to None.
        page (int, optional): Page number for pagination. Defaults to 1.
        limit (int, optional): Number of reviews per page. Defaults to 20.
        sort_by (str, optional): Field to sort by ('created_at' or 'rating'). Defaults to "created_at".
        sort_order (str, optional): Sort order, either 'asc' or 'desc'. Defaults to "desc".

    Returns:
        tuple:
            - List[Review]: List of Review ORM objects for the requested page.
            - int: Total number of reviews matching the query.
            - float: Average rating of the queried reviews.
    """
    query = db.query(Review).filter(Review.book_id == book_id)
    if rating:
        query = query.filter(Review.rating == rating)
    total = query.count()
    if sort_order == "asc":
        query = query.order_by(getattr(Review, sort_by).asc())
    else:
        query = query.order_by(getattr(Review, sort_by).desc())
    items = query.offset((page - 1) * limit).limit(limit).all()
    avg_rating = query.with_entities(func.avg(Review.rating)).scalar() or 0
    return items, total, avg_rating
