"""
Main application module for the Orders Service.

This module initializes the FastAPI application, sets basic metadata,
and includes the API router for order-related endpoints.
"""

from fastapi import FastAPI
from app.database import init_db
from app.api.v1 import orders

app = FastAPI(title="Orders Service", version="1.0")
app.include_router(orders.router)


@app.on_event("startup")
def startup():
    """
    FastAPI startup event handler.

    This function is executed when the application starts and is used to
    initialize the database tables.
    """
    init_db()


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns:
        dict: A simple JSON response indicating the service is running.
              Example: {"status": "healthy"}
    """
    return {"status": "healthy"}
