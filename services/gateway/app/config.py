"""
Configuration for API Gateway.

This module provides environment-based configuration for connecting
to the various microservices and external dependencies such as Redis
and JWT authentication.

Attributes:
    AUTH_SERVICE_URL (str): URL for the Auth Service. Defaults to "http://auth:8001".
    BOOKS_SERVICE_URL (str): URL for the Books Service. Defaults to "http://books:8002".
    ORDERS_SERVICE_URL (str): URL for the Orders Service. Defaults to "http://orders:8003".
    REVIEWS_SERVICE_URL (str): URL for the Reviews Service. Defaults to "http://reviews:8004".
    REDIS_URL (str): URL for connecting to Redis for caching and rate limiting.
                     Defaults to "redis://redis:6379/0".
    JWT_SECRET_KEY (str): Secret key used to sign and verify JWT tokens.
                          Defaults to "supersecretkey".
"""

import os

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001")
BOOKS_SERVICE_URL = os.getenv("BOOKS_SERVICE_URL", "http://books:8002")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://orders:8003")
REVIEWS_SERVICE_URL = os.getenv("REVIEWS_SERVICE_URL", "http://reviews:8004")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
PUBSUB_MODE = os.getenv("PUBSUB_MODE", "stub")
