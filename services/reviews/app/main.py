"""
HTTP endpoints for the Reviews Service.

This module defines the REST API for managing book reviews, including
creating, retrieving, updating, deleting, and summarizing review data.
It integrates with:

- PostgreSQL (via SQLAlchemy) for persistent storage
- Redis for caching high-traffic read endpoints
- A pub/sub system for emitting domain events such as review.created,
  review.updated, and review.deleted

All endpoints include descriptive docstrings summarizing their purpose,
arguments, return values, and possible HTTP exceptions.
"""

import asyncio
import json

from fastapi import Body, Depends, FastAPI, HTTPException, Request
from shared.pubsub import publish
from sqlalchemy import func

from . import db, models
from .deps import get_db, get_redis

app = FastAPI(title="Reviews Service", root_path="/api/v1/reviews")


@app.on_event("startup")
def startup():
    """
    Initialize application state during startup.

    Creates all database tables defined in the models by calling `init_db`.
    This ensures the database schema exists before handling requests.
    """
    db.init_db()


@app.get("/health")
def health():
    """
    Health-check endpoint.

    Returns:
        dict: A simple health status indicating the service is running.
    """
    return {"status": "healthy"}


@app.post("", status_code=201)
def create_review(payload: dict = Body(...), db=Depends(get_db)):
    """
    Create a new review.

    Args:
        payload (dict): Incoming JSON containing fields:
            - book_id (str)
            - user_id (str, optional)
            - rating (int)
            - title (str, optional)
            - comment (str, optional)
        db: Database session dependency.

    Returns:
        dict: The created review object including timestamps.

    Raises:
        HTTPException (400): If the user already reviewed the same book.
    """
    book_id = payload.get("book_id")
    user_id = payload.get("user_id", "anonymous")
    rating = int(payload.get("rating", 0))
    session = db

    existing = (
        session.query(models.Review)
        .filter(models.Review.book_id == book_id, models.Review.user_id == user_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already reviewed this book")

    r = models.Review(
        book_id=book_id,
        user_id=user_id,
        rating=rating,
        title=payload.get("title"),
        comment=payload.get("comment"),
    )
    session.add(r)
    session.commit()
    session.refresh(r)

    asyncio.create_task(
        publish(
            "review.created",
            {"review_id": r.id, "book_id": r.book_id, "rating": r.rating},
        )
    )

    return {
        "id": r.id,
        "book_id": r.book_id,
        "user_id": r.user_id,
        "rating": r.rating,
        "title": r.title,
        "comment": r.comment,
        "created_at": r.created_at,
    }


@app.get("/book/{book_id}")
def list_reviews(
    book_id: str,
    page: int = 1,
    limit: int = 20,
    rating: int = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db=Depends(get_db),
    redis=Depends(get_redis),
):
    """
    List reviews for a specific book.

    Supports pagination, optional rating filter, and caching.

    Args:
        book_id (str): ID of the book being queried.
        page (int): Page number for pagination.
        limit (int): Number of results per page.
        rating (int, optional): Filter by rating.
        sort_by (str): Column to sort by (unused but accepted).
        sort_order (str): Sorting direction (unused but accepted).
        db: Database session.
        redis: Redis client.

    Returns:
        dict: Paginated list of reviews with metadata and average rating.
    """
    key = f"reviews:book:{book_id}:page:{page}"
    cached = redis.get(key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    session = db
    q = session.query(models.Review).filter(models.Review.book_id == book_id)
    if rating:
        q = q.filter(models.Review.rating == rating)

    total = q.count()
    items = q.limit(limit).offset((page - 1) * limit).all()

    out = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "rating": r.rating,
            "title": r.title,
            "comment": r.comment,
            "created_at": r.created_at,
        }
        for r in items
    ]

    avg = (
        session.query(func.coalesce(func.avg(models.Review.rating), 0))
        .filter(models.Review.book_id == book_id)
        .scalar()
        or 0.0
    )

    resp = {
        "items": out,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total // limit) + (1 if total % limit else 0),
        "average_rating": float(avg),
    }

    redis.set(key, json.dumps(resp, default=str), ex=600)
    return resp


@app.get("/book/{book_id}/summary")
def summary(book_id: str, db=Depends(get_db), redis=Depends(get_redis)):
    """
    Return a summary of reviews for a given book.

    Includes total reviews, average rating, and rating distribution.

    Args:
        book_id (str): Book identifier.
        db: Database session.
        redis: Redis client.

    Returns:
        dict: Summary statistics.
    """
    key = f"reviews:summary:{book_id}"
    cached = redis.get(key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    session = db

    total = session.query(models.Review).filter(models.Review.book_id == book_id).count()

    avg = (
        session.query(func.coalesce(func.avg(models.Review.rating), 0))
        .filter(models.Review.book_id == book_id)
        .scalar()
        or 0.0
    )

    dist_q = (
        session.query(models.Review.rating, func.count(models.Review.id))
        .filter(models.Review.book_id == book_id)
        .group_by(models.Review.rating)
        .all()
    )
    dist = {str(k): v for k, v in dist_q}

    resp = {
        "book_id": book_id,
        "total_reviews": total,
        "average_rating": float(avg),
        "rating_distribution": dist,
    }

    redis.set(key, json.dumps(resp, default=str), ex=900)
    return resp


@app.get("/user/me")
def my_reviews(
    page: int = 1, limit: int = 20, db=Depends(get_db), request: Request = None
):
    """
    List reviews written by the current user.

    User identification is done via the `user_id` query parameter
    (placeholder behavior until auth is implemented).

    Args:
        page (int): Pagination page number.
        limit (int): Results per page.
        db: Database session.
        request (Request): Incoming request providing user_id.

    Returns:
        dict: Paginated list of user reviews.
    """
    user_id = request.query_params.get("user_id", "anonymous")
    session = db

    q = session.query(models.Review).filter(models.Review.user_id == user_id)
    total = q.count()
    items = q.limit(limit).offset((page - 1) * limit).all()

    out = [
        {
            "id": r.id,
            "book_id": r.book_id,
            "book_title": "",
            "rating": r.rating,
            "title": r.title,
            "created_at": r.created_at,
        }
        for r in items
    ]

    return {
        "items": out,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total // limit) + (1 if total % limit else 0),
    }


@app.get("/{review_id}")
def get_review(review_id: str, db=Depends(get_db)):
    """
    Retrieve a single review by its ID.

    Args:
        review_id (str): Unique identifier of the review.
        db: Database session.

    Returns:
        dict: The full review record.

    Raises:
        HTTPException (404): If the review does not exist.
    """
    r = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")

    return {
        "id": r.id,
        "book_id": r.book_id,
        "user_id": r.user_id,
        "rating": r.rating,
        "title": r.title,
        "comment": r.comment,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
    }


@app.put("/{review_id}")
def update_review(
    review_id: str,
    payload: dict = Body(...),
    db=Depends(get_db),
    request: Request = None,
):
    """
    Update an existing review.

    Args:
        review_id (str): ID of the review to update.
        payload (dict): Fields to update (rating, title, comment, user_id).
        db: Database session.
        request (Request): Used for fallback user identification.

    Returns:
        dict: The updated review.

    Raises:
        HTTPException (404): Review not found.
        HTTPException (403): User is not the review owner.
    """
    user_id = (
        payload.get("user_id")
        or (request.query_params.get("user_id") if request else None)
        or "anonymous"
    )

    r = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    if r.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if payload.get("rating") is not None:
        r.rating = int(payload.get("rating"))
    if payload.get("title"):
        r.title = payload.get("title")
    if payload.get("comment"):
        r.comment = payload.get("comment")

    db.add(r)
    db.commit()
    db.refresh(r)

    asyncio.create_task(publish("review.updated", {"review_id": r.id}))

    return {
        "id": r.id,
        "rating": r.rating,
        "title": r.title,
        "comment": r.comment,
        "updated_at": r.updated_at,
    }


@app.delete("/{review_id}", status_code=204)
def delete_review(review_id: str, db=Depends(get_db), request: Request = None):
    """
    Delete a review by ID.

    Args:
        review_id (str): The review to delete.
        db: Database session.
        request (Request): Provides user_id for authorization.

    Returns:
        None

    Raises:
        HTTPException (404): If the review does not exist.
        HTTPException (403): If the user is not allowed to delete it.
    """
    user_id = request.query_params.get("user_id", "anonymous")
    r = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    if r.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(r)
    db.commit()

    asyncio.create_task(publish("review.deleted", {"review_id": review_id}))
    return
