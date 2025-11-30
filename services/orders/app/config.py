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
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/orders_db"
)
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BOOKS_SERVICE_URL: str = os.getenv("BOOKS_SERVICE_URL", "http://localhost:8002")
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
