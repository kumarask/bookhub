"""
Pydantic schemas for the Reviews Service.

These schemas define the shape of request and response payloads
for the Reviews API. They provide validation and serialization
for creating, updating, retrieving, and summarizing book reviews.
"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict


class ReviewCreate(BaseModel):
    """
    Schema for creating a new review.

    Attributes:
        book_id (UUID): ID of the book being reviewed.
        rating (int): Rating given by the user (1-5).
        title (Optional[str]): Optional title for the review.
        comment (Optional[str]): Optional textual comment.
    """

    book_id: UUID
    rating: int
    title: Optional[str]
    comment: Optional[str]


class ReviewUpdate(BaseModel):
    """
    Schema for updating an existing review.

    All fields are optional to allow partial updates.
    Attributes:
        rating (Optional[int]): Updated rating.
        title (Optional[str]): Updated title.
        comment (Optional[str]): Updated comment.
    """

    rating: Optional[int]
    title: Optional[str]
    comment: Optional[str]


class ReviewOut(BaseModel):
    """
    Schema for returning review details in responses.

    Attributes:
        id (UUID): Review ID.
        book_id (UUID): ID of the reviewed book.
        user_id (UUID): ID of the user who created the review.
        username (str): Username of the reviewer.
        rating (int): Rating given.
        title (Optional[str]): Review title.
        comment (Optional[str]): Review comment.
        created_at (datetime): Timestamp of creation.
        updated_at (Optional[datetime]): Timestamp of last update.
    """

    id: UUID
    book_id: UUID
    user_id: UUID
    username: str
    rating: int
    title: Optional[str]
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserReviewsOut(BaseModel):
    """
    Schema for paginated list of a user's reviews or book reviews.

    Attributes:
        items (List[ReviewOut]): List of reviews.
        total (int): Total number of reviews.
        page (int): Current page number.
        limit (int): Number of reviews per page.
        pages (int): Total number of pages.
    """

    items: List[ReviewOut]
    total: int
    page: int
    limit: int
    pages: int


class ReviewSummaryOut(BaseModel):
    """
    Schema for aggregated review summary for a book.

    Attributes:
        book_id (UUID): ID of the book.
        total_reviews (int): Total number of reviews for the book.
        average_rating (float): Average rating.
        rating_distribution (Dict[str, int]): Number of reviews per rating (1-5).
    """

    book_id: UUID
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]
