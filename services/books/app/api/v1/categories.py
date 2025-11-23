"""
Categories API Module

This module provides endpoints to manage and retrieve book categories. 
It includes functionality to list all categories along with the number of books 
associated with each category. Category data is cached in Redis to improve performance.

Redis Caching Strategy:
-----------------------
- All categories: `categories:all` (TTL: 24 hours)
"""

import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models import categories, books
from app import schemas, database, cache

router = APIRouter(prefix="/api/v1/books/categories", tags=["Categories"])


@router.get("/", response_model=List[schemas.CategoryOut])
async def get_categories(db: Session = Depends(database.get_db)):
    """
    Retrieve a list of all book categories.

    This endpoint returns all categories in the system along with the total number
    of books in each category. Results are cached in Redis for 24 hours to 
    improve performance.

    Args:
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(database.get_db).

    Returns:
        List[schemas.CategoryOut]: A list of categories, each containing:
            - id (str): Category ID
            - name (str): Category name
            - description (str): Description of the category
            - book_count (int): Number of books associated with the category
    """
    cache_key = "categories:all"
    cached = await cache.redis_client.get(cache_key)
    if cached:
        return [schemas.CategoryOut(**c) for c in json.loads(cached)]

    categories_list = db.query(categories.Category).all()
    result = []
    for c in categories_list:
        book_count = len(c.books) if hasattr(c, "books") else db.query(books.Book).filter(books.Book.category_id == c.id).count()
        result.append({
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "book_count": book_count
        })

    await cache.redis_client.set(cache_key, json.dumps(result), ex=86400)
    return result
