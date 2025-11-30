"""
Configuration settings for the Reviews Service.

Includes database, Redis, and external service URLs.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/reviews_db"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BOOKS_SERVICE_URL = os.getenv("BOOKS_SERVICE_URL", "http://localhost:8001")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
