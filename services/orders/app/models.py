"""
Database models for the Orders Service.

This module defines the SQLAlchemy ORM models for managing orders and their items
in the Orders Service. It includes the following models:

- Order: Represents a user's order with status, total amount, and timestamps.
- OrderItem: Represents individual books/items in an order with quantity, price,
  and subtotal.

Relationships:
- One-to-many relationship from Order to OrderItem.
"""

import uuid
from sqlalchemy import (
    Column,
    String,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    """
    Represents a user's order.

    Attributes:
        id (UUID): Unique identifier for the order.
        user_id (UUID): ID of the user who placed the order.
        status (str): Current status of the order ('pending', 'processing',
            'completed', 'cancelled').
        total_amount (Decimal): Total amount for the order.
        created_at (datetime): Timestamp when the order was created.
        updated_at (datetime): Timestamp when the order was last updated.
        items (list[OrderItem]): List of items in the order.
    """

    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=False, default="pending")
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    Represents an individual item in an order.

    Attributes:
        id (UUID): Unique identifier for the order item.
        order_id (UUID): Foreign key to the parent Order.
        book_id (UUID): ID of the book being ordered.
        quantity (int): Number of units ordered.
        price_at_purchase (Decimal): Price of the book at the time of purchase.
        subtotal (Decimal): Total price for this item (quantity * price_at_purchase).
        order (Order): Reference to the parent Order.
    """

    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    book_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    order = relationship("Order", back_populates="items")
