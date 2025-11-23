"""
Configuration for Auth Service.
Handles environment variables and service settings.
"""

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/postgres"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
PUBSUB_MODE = os.getenv("PUBSUB_MODE", "stub")
