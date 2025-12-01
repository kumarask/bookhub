"""
Configuration settings for the Orders Service.

This module centralizes all configuration values for the Orders Service, including:
- Database URL
- Redis URL
- External services URLs (e.g., Books Service)
"""

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/orders_db"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
BOOKS_SERVICE_URL = os.getenv("BOOKS_SERVICE_URL", "http://localhost:8002")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
PUBSUB_MODE = os.getenv("PUBSUB_MODE", "stub")
