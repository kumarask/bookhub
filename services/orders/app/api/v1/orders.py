"""
orders.py

Orders Service API for managing user orders.

This module provides CRUD operations for orders, including creation, retrieval,
updating status, cancellation, and statistics. It integrates with the Books Service
to validate stock, updates order data in the database, caches responses in Redis,
and publishes order-related events via Pub/Sub.

Endpoints:
- POST /api/v1/orders               : Create a new order
- GET /api/v1/orders                : List user orders (with optional filtering and pagination)
- GET /api/v1/orders/{order_id}    : Get details of a specific order
- PATCH /api/v1/orders/{order_id}/status : Update order status (admin/internal only)
- DELETE /api/v1/orders/{order_id} : Cancel a pending order
- GET /api/v1/orders/stats         : Get order statistics for the user

Caching:
- Order details: order:{order_id} (TTL 10 min)
- User order history: orders:user:{user_id}:page:{page} (TTL 5 min)

Pub/Sub Events:
- order.created
- order.completed
- order.cancelled

Dependencies:
- SQLAlchemy for database interactions
- FastAPI for request handling and dependency injection
- Redis for caching
- BooksService for stock validation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
import json
from datetime import datetime

from app import schemas, crud, database, events, cache, deps
from app.services.books_service import BooksService

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])
books_service = BooksService()


@router.post("/", response_model=schemas.OrderOut, status_code=201)
async def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Create a new order for the authenticated user.

    This endpoint:
    - Validates book stock
    - Calculates total amount
    - Persists the order in the database
    - Caches the order in Redis
    - Publishes 'order.created' event

    Args:
        order (OrderCreate): Order data containing book IDs and quantities
        db (Session): Database session (dependency)
        user (dict): Current authenticated user (dependency)

    Returns:
        OrderOut: Created order with details
    """
    try:
        db_order = await crud.create_order(db, user["id"], order, books_service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await events.publish_event("order.created", {"order_id": str(db_order.id)})
    cache_key = f"order:{db_order.id}"
    await cache.set_cache(
        cache_key,
        json.dumps(json.loads(schemas.OrderOut.from_orm(db_order).json())),
        ttl=600,
    )
    return db_order


@router.get("/", response_model=list[schemas.OrderOut])
async def list_orders(
    status: str = Query(None, regex="^(pending|processing|completed|cancelled)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(database.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Retrieve the authenticated user's order history with optional status filter
    and pagination.

    Caches the results in Redis for 5 minutes.

    Args:
        status (str, optional): Filter orders by status
        page (int): Page number for pagination
        limit (int): Number of orders per page
        db (Session): Database session
        user (dict): Current authenticated user

    Returns:
        List[OrderOut]: List of orders matching the query
    """
    cache_key = f"orders:user:{user['id']}:page:{page}:status:{status}"
    cached = await cache.get_cache(cache_key)
    if cached:
        return json.loads(cached)

    items, total = crud.list_orders(db, user["id"], status, page, limit)
    await cache.set_cache(
        cache_key,
        json.dumps([json.loads(schemas.OrderOut.from_orm(o).json()) for o in items]),
        ttl=300,
    )
    return items


@router.get("/{order_id}", response_model=schemas.OrderOut)
async def get_order_detail(
    order_id: UUID,
    db: Session = Depends(database.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Retrieve details of a specific order by ID.

    Users can only access their own orders. Order details are cached for 10 minutes.

    Args:
        order_id (UUID): Order ID
        db (Session): Database session
        user (dict): Current authenticated user

    Returns:
        OrderOut: Order details
    """
    cache_key = f"order:{order_id}"
    cached = await cache.get_cache(cache_key)
    if cached:
        order = json.loads(cached)
    else:
        order_obj = crud.get_order(db, str(order_id))
        if not order_obj:
            raise HTTPException(status_code=404, detail="Order not found")
        order = json.loads(schemas.OrderOut.from_orm(order_obj).json())
        await cache.set_cache(cache_key, json.dumps(order), ttl=600)

    if str(order["user_id"]) != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return order


@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
async def update_order_status(
    order_id: UUID,
    payload: schemas.OrderStatusUpdate,
    db: Session = Depends(database.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Update the status of an order.

    Only admin or internal services can update status. Publishes events:
    - 'order.completed' when status changes to completed
    - 'order.cancelled' when status changes to cancelled

    Args:
        order_id (UUID): Order ID
        payload (OrderStatusUpdate): New status
        db (Session): Database session
        user (dict): Current authenticated user

    Returns:
        OrderOut: Updated order
    """
    order = crud.get_order(db, str(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden")

    valid_transitions = {
        "pending": ["processing", "cancelled"],
        "processing": ["completed"],
        "completed": [],
        "cancelled": [],
    }

    if payload.status not in valid_transitions[order.status]:
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = payload.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    if payload.status == "completed":
        await events.publish_event("order.completed", {"order_id": str(order.id)})
    elif payload.status == "cancelled":
        await events.publish_event("order.cancelled", {"order_id": str(order.id)})

    cache_key = f"order:{order_id}"
    await cache.set_cache(
        cache_key,
        json.dumps(json.loads(schemas.OrderOut.from_orm(order).json())),
        ttl=600,
    )

    return order


@router.delete("/{order_id}", response_model=dict)
async def cancel_order(
    order_id: UUID,
    db: Session = Depends(database.get_db),
    user=Depends(deps.get_current_user_dep),
):
    """
    Cancel a pending order.

    Only the order owner or admin can cancel. Publishes 'order.cancelled' event.

    Args:
        order_id (UUID): Order ID
        db (Session): Database session
        user (dict): Current authenticated user

    Returns:
        dict: Confirmation message with order ID and new status
    """
    order = crud.get_order(db, str(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if str(order.user_id) != user["id"] and not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden")

    if order.status != "pending":
        raise HTTPException(
            status_code=400, detail="Cannot cancel order (already processing/completed)"
        )

    order.status = "cancelled"
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    await events.publish_event("order.cancelled", {"order_id": str(order.id)})

    cache_key = f"order:{order_id}"
    await cache.set_cache(
        cache_key,
        json.dumps(json.loads(schemas.OrderOut.from_orm(order).json())),
        ttl=600,
    )

    return {
        "id": str(order.id),
        "status": order.status,
        "message": "Order cancelled successfully",
    }


@router.get("/stats", response_model=schemas.OrderStatsOut)
async def get_order_stats(
    db: Session = Depends(database.get_db), user=Depends(deps.get_current_user_dep)
):
    """
    Get order statistics for the authenticated user.

    Returns totals for:
    - Orders by status
    - Total orders
    - Total amount spent
    - Total books purchased

    Args:
        db (Session): Database session
        user (dict): Current authenticated user

    Returns:
        OrderStatsOut: Aggregated order statistics
    """
    orders, _ = crud.list_orders(
        db, user["id"], page=1, limit=1000
    )  # fetch all user orders
    total_orders = len(orders)
    total_spent = sum(float(o.total_amount) for o in orders)
    orders_by_status = {"pending": 0, "processing": 0, "completed": 0, "cancelled": 0}
    total_books = 0
    for o in orders:
        orders_by_status[o.status] += 1
        total_books += sum(i.quantity for i in o.items)

    return schemas.OrderStatsOut(
        total_orders=total_orders,
        total_spent=total_spent,
        orders_by_status=orders_by_status,
        total_books_purchased=total_books,
    )
