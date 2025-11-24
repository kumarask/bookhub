"""
Main FastAPI application for the Auth Service.

This module initializes the FastAPI app, includes API routers for authentication
and user management, and defines application-level startup events and health
check endpoints.
"""

from fastapi import FastAPI
from app.database import init_db
from app.api.v1 import auth, user

app = FastAPI(title="Auth Service", version="1.0.0")

app.include_router(auth.router, tags=["auth"])
app.include_router(user.router, tags=["user"])


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
