"""
FastAPI Router for Reviews Service.

This module provides endpoints for managing book reviews and ratings, including:

- Creating, updating, and deleting reviews
- Retrieving reviews by book or by user
- Getting aggregated review statistics per book

Features:
- Redis caching for review lists, user reviews, and summaries
- Pub/Sub events for review.created, review.updated, review.deleted
- Authorization checks to ensure users can only modify their own reviews (except admins)
- Pagination, sorting, and filtering support
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import json
from uuid import UUID

from app import (
    schemas,
    crud,
    cache,
    deps,
    pubsub,
)

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


@router.post("/", response_model=schemas.ReviewOut, status_code=201)
async def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(deps.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Create a review for a book.

    Validates that the user has not already reviewed the book. Publishes a
    `review.created` event and clears related cached pages and summary.

    Args:
        review (schemas.ReviewCreate): Review data to create.
        db (Session): Database session dependency.
        user (dict): Authenticated user information.

    Raises:
        HTTPException: If user has already reviewed the book (400).

    Returns:
        schemas.ReviewOut: The created review.
    """

    try:
        db_review = crud.create_review(db, review, user["id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Publish event
    await pubsub.publish("review.created", {"review_id": str(db_review.id)})

    # Clear cache
    await cache.delete_cache(f"reviews:book:{review.book_id}:page:1")
    await cache.delete_cache(f"reviews:summary:{review.book_id}")

    return db_review


@router.get("/book/{book_id}", response_model=schemas.UserReviewsOut)
async def list_book_reviews(
    book_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    rating: int = Query(None, ge=1, le=5),
    sort_by: str = Query("created_at", regex="^(created_at|rating)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(deps.get_db),
):
    """
    Retrieve paginated reviews for a specific book.

    Supports optional rating filter, sorting by 'created_at' or 'rating', and caches results per page.

    Args:
        book_id (UUID): Book ID to fetch reviews for.
        page (int): Page number (default 1).
        limit (int): Number of reviews per page (default 20).
        rating (int, optional): Filter reviews by rating (1-5).
        sort_by (str): Field to sort by ('created_at' or 'rating').
        sort_order (str): Sort order ('asc' or 'desc').
        db (Session): Database session dependency.

    Returns:
        dict: Paginated review data including items, total count, pages, and current page.
    """

    cache_key = f"reviews:book:{book_id}:page:{page}:rating:{rating}:sort:{sort_by}:{sort_order}"
    cached = await cache.get_cache(cache_key)
    if cached:
        return json.loads(cached)

    items, total, _ = crud.list_reviews_by_book(
        db, str(book_id), rating, page, limit, sort_by, sort_order
    )

    pages = (total + limit - 1) // limit
    response = {
        "items": [schemas.ReviewOut.from_orm(i).dict() for i in items],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }

    await cache.set_cache(cache_key, json.dumps(response), ttl=600)
    return response


@router.get("/{review_id}", response_model=schemas.ReviewOut)
async def get_review_detail(review_id: UUID, db: Session = Depends(deps.get_db)):
    """
    Retrieve a single review by its ID.

    Args:
        review_id (UUID): Review ID to retrieve.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If review not found (404).

    Returns:
        schemas.ReviewOut: The requested review.
    """

    review = crud.get_review(db, str(review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/{review_id}", response_model=schemas.ReviewOut)
async def update_review(
    review_id: UUID,
    data: schemas.ReviewUpdate,
    db: Session = Depends(deps.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Update a user's own review.

    Only the review owner or admin can update. Publishes a `review.updated` event
    and clears relevant caches.

    Args:
        review_id (UUID): Review ID to update.
        data (schemas.ReviewUpdate): Fields to update.
        db (Session): Database session dependency.
        user (dict): Authenticated user info.

    Raises:
        HTTPException: If review not found (404) or user is not authorized (403).

    Returns:
        schemas.ReviewOut: The updated review.
    """

    review = crud.get_review(db, str(review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if str(review.user_id) != user["id"] and not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden")

    review = crud.update_review(db, review, data)

    await pubsub.publish("review.updated", {"review_id": str(review.id)})

    # Clear cache
    await cache.delete_cache(f"reviews:book:{review.book_id}:page:1")
    await cache.delete_cache(f"reviews:summary:{review.book_id}")
    await cache.delete_cache(f"reviews:user:{review.user_id}:page:1")

    return review


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    db: Session = Depends(deps.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Delete a user's own review (admin can delete any review).

    Publishes a `review.deleted` event and clears relevant caches.

    Args:
        review_id (UUID): Review ID to delete.
        db (Session): Database session dependency.
        user (dict): Authenticated user info.

    Raises:
        HTTPException: If review not found (404) or user is not authorized (403).

    Returns:
        None (204 No Content)
    """

    review = crud.get_review(db, str(review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if str(review.user_id) != user["id"] and not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden")

    crud.delete_review(db, review)

    await pubsub.publish("review.deleted", {"review_id": str(review.id)})

    # Clear cache
    await cache.delete_cache(f"reviews:book:{review.book_id}:page:1")
    await cache.delete_cache(f"reviews:summary:{review.book_id}")
    await cache.delete_cache(f"reviews:user:{review.user_id}:page:1")


@router.get("/user/me", response_model=schemas.UserReviewsOut)
async def get_my_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Retrieve paginated reviews of the authenticated user.

    Caches per page results.

    Args:
        page (int): Page number (default 1).
        limit (int): Number of reviews per page (default 20).
        db (Session): Database session dependency.
        user (dict): Authenticated user info.

    Returns:
        dict: Paginated user review data including items, total count, pages, and current page.
    """

    cache_key = f"reviews:user:{user['id']}:page:{page}"
    cached = await cache.get_cache(cache_key)
    if cached:
        return json.loads(cached)

    query = db.query(crud.Review).filter(crud.Review.user_id == user["id"])
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = (total + limit - 1) // limit

    response = {
        "items": [schemas.ReviewOut.from_orm(i).dict() for i in items],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }

    await cache.set_cache(cache_key, json.dumps(response), ttl=600)
    return response


@router.get("/book/{book_id}/summary", response_model=schemas.ReviewSummaryOut)
async def get_book_review_summary(
    book_id: UUID, db: Session = Depends(deps.get_db)
):
    """
    Retrieve aggregated review statistics for a book.

    Calculates total reviews, average rating, and rating distribution.
    Caches summary for 15 minutes.

    Args:
        book_id (UUID): Book ID to summarize reviews for.
        db (Session): Database session dependency.

    Returns:
        dict: Review summary containing total_reviews, average_rating, and rating_distribution.
    """

    cache_key = f"reviews:summary:{book_id}"
    cached = await cache.get_cache(cache_key)
    if cached:
        return json.loads(cached)

    items, total, avg_rating = crud.list_reviews_by_book(
        db, str(book_id), page=1, limit=1000
    )
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    for r in items:
        rating_distribution[str(r.rating)] += 1

    response = {
        "book_id": str(book_id),
        "total_reviews": total,
        "average_rating": float(avg_rating),
        "rating_distribution": rating_distribution,
    }

    await cache.set_cache(cache_key, json.dumps(response), ttl=900)
    return response
