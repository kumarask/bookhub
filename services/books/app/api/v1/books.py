"""
Books API Module

This module provides endpoints for managing books in the system, including:
- Creating, updating, retrieving, and deleting books
- Listing books with filters, pagination, and sorting
- Updating book stock (internal use)
- Caching book details and listings in Redis
- Publishing events for book creation, update, deletion, and low stock notifications

Redis Caching Strategy:
-----------------------
- Book details: `book:{book_id}` (TTL: 1 hour)
- Book listings: `books:list:{page}:{filters_hash}` (TTL: 15 minutes)

Pub/Sub Events:
---------------
- Published:
    - `book.created`: When a new book is added
    - `book.updated`: When a book is updated
    - `book.deleted`: When a book is deleted
    - `book.stock_low`: When stock falls below threshold (10 units)
- Subscribed:
    - `order.completed`: Update stock quantity
"""

import json
from hashlib import md5
from uuid import UUID
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import schemas, crud, events, auth, deps, cache
from app.models import books as book_models, categories as category_models

router = APIRouter(prefix="/api/v1/books", tags=["Books"])


@router.post("/", response_model=schemas.BookOut)
async def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(deps.get_db),
    user=Depends(auth.admin_required),
):
    """
    Create a new book (Admin only).

    Args:
        book (schemas.BookCreate): Book creation data
        db (Session, optional): Database session. Defaults to Depends(deps.get_db)
        user: Admin user (injected via dependency)

    Raises:
        HTTPException: If the book cannot be created (400 Bad Request)

    Returns:
        schemas.BookOut: Created book object
    """
    try:
        db_book = crud.create_book(db, book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Publish event
    await events.publish_event("book.created", {"id": str(db_book.id)})

    # Cache book detail
    cache_key = f"book:{db_book.id}"
    await cache.set_cached_book(
        cache_key,
        json.dumps(jsonable_encoder(db_book)),
        ttl=3600,
    )

    return schemas.BookOut.from_orm(db_book)


@router.get("/", response_model=schemas.BookListOut)
async def list_books(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    author: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query("title", regex="^(price|title|published_date)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    """
    List books with optional filters, pagination, and sorting.

    Args:
        db (Session, optional): Database session
        page (int): Page number (default 1)
        limit (int): Page size (default 20, max 100)
        category (str, optional): Filter by category
        author (str, optional): Filter by author
        search (str, optional): Search in title or description
        min_price (float, optional): Minimum price filter
        max_price (float, optional): Maximum price filter
        sort_by (str, optional): Field to sort by (price, title, published_date)
        sort_order (str, optional): Sort order (asc or desc)

    Returns:
        schemas.BookListOut: Paginated list of books with metadata
    """
    # Create a filters hash for caching
    filters = json.dumps(
        {
            "category": category,
            "author": author,
            "search": search,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
        sort_keys=True,
    )
    filters_hash = md5(filters.encode()).hexdigest()
    cache_key = f"books:list:{page}:{filters_hash}"

    cached = await cache.get_cached_book(cache_key)
    if cached:
        return json.loads(cached)

    # Query
    query = db.query(book_models.Book)
    if category:
        query = query.join(category_models.Category).filter(
            category_models.Category.name == category
        )
    if author:
        query = query.filter(book_models.Book.author.ilike(f"%{author}%"))
    if search:
        query = query.filter(
            book_models.Book.title.ilike(f"%{search}%")
            | book_models.Book.description.ilike(f"%{search}%")
        )
    if min_price is not None:
        query = query.filter(book_models.Book.price >= min_price)
    if max_price is not None:
        query = query.filter(book_models.Book.price <= max_price)

    sort_col = getattr(book_models.Book, sort_by)
    if sort_order == "desc":
        sort_col = sort_col.desc()
    query = query.order_by(sort_col)

    total = query.count()
    skip = (page - 1) * limit
    books = query.offset(skip).limit(limit).all()

    items = []
    for b in books:
        item = schemas.BookOut.from_orm(b)
        if b.category:
            item.category = b.category.name
        items.append(item)

    result = schemas.BookListOut(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit,
    )

    await cache.set_cached_book(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ttl=900
    )
    return result


@router.get("/{book_id}", response_model=schemas.BookDetailOut)
async def get_book_detail(book_id: UUID, db: Session = Depends(deps.get_db)):
    """
    Get detailed information of a book by ID.

    Args:
        book_id (UUID): The unique identifier of the book
        db (Session, optional): Database session

    Raises:
        HTTPException: If the book is not found (404)

    Returns:
        schemas.BookDetailOut: Detailed book object
    """
    cache_key = f"book:{book_id}"
    cached = await cache.get_cached_book(cache_key)
    if cached:
        return json.loads(cached)

    db_book = crud.get_book(db, str(book_id))
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_detail = schemas.BookDetailOut.from_orm(db_book)
    await cache.set_cached_book(
        cache_key,
        json.dumps(jsonable_encoder(book_detail)),
        ttl=3600,
    )
    return book_detail


@router.put("/{book_id}", response_model=schemas.BookOut)
async def update_book(
    book_id: UUID,
    updates: schemas.BookUpdate,
    db: Session = Depends(deps.get_db),
    user=Depends(auth.admin_required),
):
    """
    Update a book (Admin only).

    Args:
        book_id (UUID): Book ID to update
        updates (schemas.BookUpdate): Fields to update
        db (Session, optional): Database session
        user: Admin user (injected via dependency)

    Raises:
        HTTPException: If the book is not found (404)

    Returns:
        schemas.BookOut: Updated book object
    """
    db_book = crud.get_book(db, str(book_id))
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_book, field, value)
    db_book.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_book)

    # Publish event
    await events.publish_event("book.updated", {"id": str(db_book.id)})

    # Update cache
    cache_key = f"book:{book_id}"
    await cache.set_cached_book(
        cache_key,
        json.dumps(jsonable_encoder(db_book)),
        ttl=3600,
    )

    return schemas.BookOut.from_orm(db_book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: UUID,
    db: Session = Depends(deps.get_db),
    user=Depends(auth.admin_required),
):
    """
    Delete a book (Admin only).

    Args:
        book_id (UUID): Book ID to delete
        db (Session, optional): Database session
        user: Admin user (injected via dependency)

    Raises:
        HTTPException: If the book is not found (404)

    Returns:
        None
    """
    db_book = crud.get_book(db, str(book_id))
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    crud.delete_book(db, db_book)

    # Publish event
    await events.publish_event("book.deleted", {"id": str(book_id)})

    # Delete cache
    cache_key = f"book:{book_id}"
    await cache.delete_cached_book(cache_key)


@router.patch("/{book_id}/stock", response_model=schemas.BookStockOut)
async def update_stock(
    book_id: UUID,
    payload: schemas.BookStockUpdate,
    db: Session = Depends(deps.get_db),
    _=Depends(deps.verify_internal_secret),
):
    """
    Update book stock (Internal use only).

    Args:
        book_id (UUID): Book ID to update stock
        payload (schemas.BookStockUpdate): Quantity change
        db (Session, optional): Database session
        _ : Internal service secret validation dependency

    Raises:
        HTTPException: If the book is not found (404) or insufficient stock (400)

    Returns:
        schemas.BookStockOut: Updated stock info of the book
    """
    db_book = crud.get_book(db, str(book_id))
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    new_stock = db_book.stock_quantity + payload.quantity_change
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    db_book.stock_quantity = new_stock
    db_book.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_book)

    if db_book.stock_quantity < 10:
        await events.publish_event(
            "book.stock_low",
            {"id": str(db_book.id), "stock_quantity": db_book.stock_quantity},
        )

    cache_key = f"book:{book_id}"
    await cache.set_cached_book(
        cache_key,
        json.dumps(jsonable_encoder(db_book)),
        ttl=3600,
    )

    return schemas.BookStockOut(
        id=db_book.id,
        stock_quantity=db_book.stock_quantity,
        updated_at=db_book.updated_at,
    )
