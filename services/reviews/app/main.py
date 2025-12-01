"""
Main entry point for the Reviews Service.

This module initializes the FastAPI application, sets the service title and version,
and includes the API router for version 1 of the reviews endpoints.
"""

from fastapi import FastAPI
from app.api.v1 import reviews
from app.database import init_db

app = FastAPI(title="Reviews Service", version="1.0")
app.include_router(reviews.router)


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
