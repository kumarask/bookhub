"""
Main application module for the Orders Service.

This module initializes the FastAPI application, sets basic metadata,
and includes the API router for order-related endpoints.
"""

from fastapi import FastAPI
from app.api.v1 import orders

app = FastAPI(title="Orders Service", version="1.0")
app.include_router(orders.router)
