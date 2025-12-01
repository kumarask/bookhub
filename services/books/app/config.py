"""
Configuration module for application settings.

This module loads environment-specific configuration values such as JWT secrets,
algorithms, Redis connection URL, and database connection string. It uses
environment variables when available, falling back to default values for local
development.
"""

import os


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
REDIS_URL = "redis://redis:6379"
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@postgres:5432/booksdb"
)
INTERNAL_SECRET = "supersecretinternalkey"
AUTH_SERVICE_URL = "http://auth:8001"
PUBSUB_MODE = os.getenv("PUBSUB_MODE", "stub")
