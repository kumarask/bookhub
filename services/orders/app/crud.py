"""
app.crud.orders

CRUD operations for the Orders service.

This module provides functions to create orders, retrieve a single order,
and list orders for a specific user with optional status filtering and pagination.

Functions
---------
- create_order(db: Session, user_id: str, order: OrderCreate, books_service) -> Order
    Creates a new order, validates stock, reduces stock, calculates totals, and stores order items.
- get_order(db: Session, order_id: str) -> Order | None
    Retrieve a single order by its ID.
- list_orders(db: Session, user_id: str, status: str = None, page: int = 1, limit: int = 20) -> tuple[list[Order], int]
    List orders for a user with optional status filter and pagination.
"""

from sqlalchemy.orm import Session
from app import models as order_models
from app.schemas import OrderCreate


async def create_order(db: Session, user_id: str, order: OrderCreate, books_service):
    """
    Create a new order for a user.

    This function performs the following steps:
    1. Validates stock for each book in the order.
    2. Calculates subtotal for each item and the total amount for the order.
    3. Stores the order and associated order items in the database.
    4. Reduces the stock quantity for each book using the BooksService.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (str): The ID of the user placing the order.
        order (OrderCreate): Order data including items and quantities.
        books_service (BooksService): Service to interact with book stock and details.

    Raises:
        ValueError: If a book_id is invalid or stock is insufficient.

    Returns:
        Order: The created Order object with associated items.

    Example:
        >>> from app.crud.orders import create_order
        >>> from app.schemas import OrderCreate, OrderItemCreate
        >>> from app.services.books_service import BooksService
        >>> import asyncio
        >>>
        >>> async def main():
        >>>     books_service = BooksService()
        >>>     order_data = OrderCreate(items=[
        >>>         OrderItemCreate(book_id="660e8400-e29b-41d4-a716-446655440001", quantity=2),
        >>>         OrderItemCreate(book_id="660e8400-e29b-41d4-a716-446655440002", quantity=1)
        >>>     ])
        >>>     new_order = await create_order(db_session, user_id="550e8400-e29b-41d4-a716-446655440000", order=order_data, books_service=books_service)
        >>>     print(new_order.id)
        >>>
        >>> asyncio.run(main())
    """
    total = 0
    items_data = []

    for item in order.items:
        book = await books_service.get_book(item.book_id)
        if not book:
            raise ValueError(f"Invalid book_id {item.book_id}")
        if book["stock_quantity"] < item.quantity:
            raise ValueError(f"Insufficient stock for {book['title']}")
        subtotal = item.quantity * book["price"]
        total += subtotal
        items_data.append(
            {
                "book_id": item.book_id,
                "quantity": item.quantity,
                "price_at_purchase": book["price"],
                "subtotal": subtotal,
            }
        )

    db_order = order_models.Order(user_id=user_id, status="pending", total_amount=total)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item_data in items_data:
        db_item = order_models.OrderItem(order_id=db_order.id, **item_data)
        db.add(db_item)
        # Reduce stock
        await books_service.update_stock(item_data["book_id"], -item_data["quantity"])
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: str):
    """
    Retrieve a single order by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        order_id (str): The ID of the order.

    Returns:
        Order | None: The Order object if found, else None.
    """
    return (
        db.query(order_models.Order).filter(order_models.Order.id == order_id).first()
    )


def list_orders(
    db: Session, user_id: str, status: str = None, page: int = 1, limit: int = 20
):
    """
    List orders for a specific user with optional status filter and pagination.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (str): The ID of the user whose orders are being queried.
        status (str, optional): Filter by order status ('pending', 'processing', 'completed', 'cancelled').
        page (int, optional): Page number for pagination (default 1).
        limit (int, optional): Number of orders per page (default 20).

    Returns:
        tuple[list[Order], int]: A tuple containing the list of orders and the total count.
    """
    query = db.query(order_models.Order).filter(order_models.Order.user_id == user_id)
    if status:
        query = query.filter(order_models.Order.status == status)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total
