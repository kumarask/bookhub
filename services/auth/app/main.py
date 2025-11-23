"""
Main FastAPI app for Auth Service.
"""

from fastapi import FastAPI
from app.database import init_db
from app.api.v1 import auth, user

app = FastAPI(title="Auth Service", version="1.0.0")

# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(user.router, tags=["user"])


@app.on_event("startup")
def startup():
    """Startup event to initialize database."""
    init_db()

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


