"""
Main entry point for the Reviews Service.

This module initializes the FastAPI application, sets the service title and version,
and includes the API router for version 1 of the reviews endpoints.
"""

from fastapi import FastAPI
from app.api.v1 import reviews

app = FastAPI(title="Reviews Service", version="1.0")
app.include_router(reviews.router)
