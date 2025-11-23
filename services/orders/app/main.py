"""Orders service HTTP endpoints.

This module implements the Orders service HTTP API. It provides
endpoints to create, list, retrieve, update, cancel orders, and to
retrieve aggregate statistics. When orders are created, updated or
cancelled the service publishes lightweight domain events (for example
``order.created``, ``order.updated``, ``order.cancelled``) via the
shared pub/sub helper so other services (inventory, billing, notifications)
can react asynchronously.

The implementation in this scaffold performs basic validation and uses
the books service to verify availability and pricing at order creation
time. Handlers use a SQLAlchemy session dependency for persistence and
schedule background publishing of events with ``asyncio.create_task``.

Consider enhancing this module by:
- adding authentication and authorization (associate orders with users),
- introducing stronger request validation with Pydantic models, and
- replacing synchronous HTTP calls with resilient clients or retry logic.
"""

import asyncio

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException
from shared.pubsub import publish
from sqlalchemy import func

from . import db, models
from .deps import get_db
from .models import Order, OrderItem

app = FastAPI(title="Orders Service", root_path="/api/v1/orders")


@app.on_event("startup")
def startup():
    """Initialize database tables when the application starts.

    This callback is executed on FastAPI startup and ensures that the
    SQLAlchemy models have their corresponding tables created in the
    configured database.
    """
    db.init_db()  # create tables


@app.get("/health")
def health():
    """Return simple health status for the service.

    Returns:
        dict: A mapping containing the service status.
    """
    return {"status": "healthy"}



@app.post("", status_code=201)
def create_order(payload: dict = Body(...), db=Depends(get_db)):
    """Create a new order and persist it to the database.

    The function validates requested items by querying the books
    service for availability and price. If validation succeeds an
    Order and corresponding OrderItem rows are created. A
    background task is scheduled to publish an "order.created" event.

    Args:
        payload (dict): Request payload containing at least an
            ``items`` list and an optional ``user_id``.
        db: SQLAlchemy session provided by dependency injection.

    Returns:
        dict: Created order summary including id, user_id, status and
            timestamps.

    Raises:
        HTTPException: If items are missing, a book is invalid or
            insufficient stock is available.
    """
    items = payload.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="No items")
    session = db
    total = 0.0
    
    book_details = {}
    for it in items:
        book_id = it.get("book_id")
        qty = int(it.get("quantity", 1))
        r = httpx.get(f"http://books:8002/api/v1/books/{book_id}")
        if r.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Invalid book_id or unavailable"
            )
        b = r.json()
        if b.get("stock_quantity", 0) < qty:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        book_details[book_id] = b
        total += b.get("price", 0.0) * qty
    

    order = Order(
        user_id=payload.get("user_id", "anonymous"),
        status="pending",
        total_amount=total,
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    for it in items:
        book_id = it.get("book_id")
        qty = int(it.get("quantity", 1))
        b = book_details[book_id]
        oi = OrderItem(
            order_id=order.id,
            book_id=book_id,
            quantity=qty,
            price_at_purchase=b.get("price", 0.0),
            subtotal=b.get("price", 0.0) * qty,
        )
        session.add(oi)
    session.commit()
    asyncio.create_task(
        publish("order.created", {"order_id": order.id, "user_id": order.user_id})
    )
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "items": [],
        "total_amount": order.total_amount,
        "created_at": order.created_at,
    }


@app.get("")
def list_orders(page: int = 1, limit: int = 20, status: str = None, db=Depends(get_db)):
    """Return a paginated list of orders.

    Args:
        page (int): Page number (1-indexed).
        limit (int): Number of items per page.
        status (str | None): Optional status filter.
        db: SQLAlchemy session provided by dependency injection.

    Returns:
        dict: A pagination object containing items, total and paging
            metadata.
    """
    session = db
    q = session.query(models.Order)
    if status:
        q = q.filter(models.Order.status == status)
    total = q.count()
    items = q.limit(limit).offset((page - 1) * limit).all()
    out = []
    for o in items:
        cnt = (
            session.query(models.OrderItem)
            .filter(models.OrderItem.order_id == o.id)
            .count()
        )
        out.append(
            {
                "id": o.id,
                "status": o.status,
                "total_amount": o.total_amount,
                "item_count": cnt,
                "created_at": o.created_at,
                "updated_at": o.updated_at,
            }
        )
    return {
        "items": out,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total // limit) + (1 if total % limit else 0),
    }


@app.get("/{order_id}")
def get_order(order_id: str, db=Depends(get_db)):
    """Retrieve a single order by its identifier.

    Args:
        order_id (str): The UUID or identifier of the order.
        db: SQLAlchemy session provided by dependency injection.

    Returns:
        dict: Detailed order information including items and totals.

    Raises:
        HTTPException: If the order does not exist (404).
    """
    session = db
    o = session.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    items = (
        session.query(models.OrderItem).filter(models.OrderItem.order_id == o.id).all()
    )
    its = []
    for it in items:
        its.append(
            {
                "id": it.id,
                "book_id": it.book_id,
                "quantity": it.quantity,
                "price_at_purchase": it.price_at_purchase,
                "subtotal": it.subtotal,
            }
        )
    return {
        "id": o.id,
        "user_id": o.user_id,
        "status": o.status,
        "items": its,
        "total_amount": o.total_amount,
        "created_at": o.created_at,
        "updated_at": o.updated_at,
    }


@app.patch("/{order_id}/status")
def update_status(order_id: str, payload: dict = Body(...), db=Depends(get_db)):
    """Update an order's status.

    Valid status values are ``pending``, ``processing``, ``completed``
    and ``cancelled``. When the status changes an event is published
    to notify other services.

    Args:
        order_id (str): Order identifier.
        payload (dict): Payload containing the new ``status`` value.
        db: SQLAlchemy session provided by dependency injection.

    Returns:
        dict: A small object with the order id, new status and update
            timestamp.

    Raises:
        HTTPException: If the provided status is invalid or the order
            does not exist.
    """
    new_status = payload.get("status")
    if new_status not in ["pending", "processing", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    session = db
    o = session.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    o.status = new_status
    session.add(o)
    session.commit()
    session.refresh(o)
    asyncio.create_task(
        publish(
            "order.completed" if new_status == "completed" else "order.updated",
            {"order_id": o.id, "status": new_status},
        )
    )
    return {"id": o.id, "status": o.status, "updated_at": o.updated_at}


@app.delete("/{order_id}")
def cancel_order(order_id: str, db=Depends(get_db)):
    """Cancel a pending order.

    Only orders in ``pending`` state may be cancelled. Cancelling an
    order sets its status to ``cancelled`` and publishes an
    ``order.cancelled`` event.

    Args:
        order_id (str): Order identifier.
        db: SQLAlchemy session provided by dependency injection.

    Returns:
        dict: Confirmation object containing id, status and a message.

    Raises:
        HTTPException: If the order does not exist or is not in a
            cancellable state.
    """
    session = db
    o = session.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    if o.status != "pending":
        raise HTTPException(
            status_code=400, detail="Cannot cancel order (already processing/completed)"
        )
    o.status = "cancelled"
    session.add(o)
    session.commit()
    asyncio.create_task(publish("order.cancelled", {"order_id": o.id}))
    return {
        "id": o.id,
        "status": "cancelled",
        "message": "Order cancelled successfully",
    }


@app.get("/stats")
def stats(db=Depends(get_db)):
    """Return aggregate statistics for orders.

    The statistics include total order count, total amount spent,
    a breakdown by status and total number of books purchased.

    Args:
        db: SQLAlchemy session provided by dependency injection.

    Returns:
        dict: Aggregated statistics values.
    """
    session = db
    total = session.query(models.Order).count()
    total_spent = (
        session.query(models.Order)
        .with_entities(func.coalesce(func.sum(models.Order.total_amount), 0))
        .scalar()
        or 0.0
    )
    
    s = (
        session.query(models.Order.status, func.count(models.Order.id))
        .group_by(models.Order.status)
        .all()
    )
    by_status = {k: v for k, v in s}
    total_books = (
        session.query(models.OrderItem)
        .with_entities(func.coalesce(func.sum(models.OrderItem.quantity), 0))
        .scalar()
        or 0
    )
    return {
        "total_orders": total,
        "total_spent": float(total_spent),
        "orders_by_status": by_status,
        "total_books_purchased": int(total_books),
    }
