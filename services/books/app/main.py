"""
Main FastAPI application entry point for the Books Service.

This module initializes the FastAPI app instance, sets its metadata,
and includes API routers for version 1 endpoints. It serves as the
central point for mounting all application routes.

Components:
    - app: FastAPI application instance.
    - books.router: Router containing book-related endpoints.
    - categories.router: Router containing category-related endpoints.
"""

from fastapi import FastAPI
from app.api.v1 import books, categories

app = FastAPI(title="Books Service", version="1.0")

# Include API routers
app.include_router(books.router)
app.include_router(categories.router)
