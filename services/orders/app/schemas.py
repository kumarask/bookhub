"""
Pydantic schemas for the Orders Service.

This module defines request and response models for the Orders Service API.
It includes schemas for creating orders, returning order details, updating
order status, and aggregating order statistics.

Schemas:
- OrderItemCreate: Represents a book item in an order creation request.
- OrderCreate: Represents an order creation request.
- OrderItemOut: Represents a single book item in the order response.
- OrderOut: Represents an order with details, items, and totals.
- OrderStatusUpdate: Represents a request to update the status of an order.
- OrderStatsOut: Represents aggregated order statistics for a user.

Author: Your Name
"""

from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class OrderItemCreate(BaseModel):
    """
    Schema for creating a single item in an order.

    Attributes:
        book_id (UUID): ID of the book to order.
        quantity (int): Number of units to order.
    """

    book_id: UUID
    quantity: int


class OrderCreate(BaseModel):
    """
    Schema for creating a new order.

    Attributes:
        items (List[OrderItemCreate]): List of items to include in the order.
    """

    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    """
    Schema for a single order item in the response.

    Attributes:
        id (UUID): Unique identifier for the order item.
        book_id (UUID): ID of the book.
        book_title (str): Title of the book.
        quantity (int): Number of units ordered.
        price_at_purchase (float): Price per unit at the time of purchase.
        subtotal (float): Total cost for this item (quantity * price_at_purchase).
    """

    id: UUID
    book_id: UUID
    book_title: str
    quantity: int
    price_at_purchase: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    """
    Schema for an order response including all items.

    Attributes:
        id (UUID): Unique identifier for the order.
        user_id (UUID): ID of the user who placed the order.
        status (str): Current status of the order.
        items (List[OrderItemOut]): List of items in the order.
        total_amount (float): Total amount for the order.
        created_at (datetime): Timestamp when the order was created.
        updated_at (datetime): Timestamp when the order was last updated.
    """

    id: UUID
    user_id: UUID
    status: str
    items: List[OrderItemOut]
    total_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """
    Schema for updating the status of an order.

    Attributes:
        status (str): New status for the order.
    """

    status: str


class OrderStatsOut(BaseModel):
    """
    Schema for order statistics for a user.

    Attributes:
        total_orders (int): Total number of orders.
        total_spent (float): Total amount spent across all orders.
        orders_by_status (dict): Count of orders by status.
        total_books_purchased (int): Total number of books purchased.
    """

    total_orders: int
    total_spent: float
    orders_by_status: dict
    total_books_purchased: int
