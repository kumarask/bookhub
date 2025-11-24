"""
Configuration module for the Auth Service.

This module centralizes environment variables and service settings used
throughout the authentication service. It provides default values for
database connections, Redis, JWT settings, token expiration times, and
pub/sub mode, while allowing overrides via environment variables.

Settings:
    DATABASE_URL (str): SQLAlchemy database URL.
    REDIS_URL (str): Redis connection URL.
    JWT_SECRET_KEY (str): Secret key used for signing JWT tokens.
    JWT_ALGORITHM (str): Algorithm used for JWT encoding/decoding.
    ACCESS_TOKEN_EXPIRE_MINUTES (int): Expiration time for access tokens.
    REFRESH_TOKEN_EXPIRE_DAYS (int): Expiration time for refresh tokens.
    PUBSUB_MODE (str): Pub/Sub mode ("stub" or actual implementation).
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
