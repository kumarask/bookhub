"""
Database utilities for the Auth Service using SQLAlchemy.

This module provides the database engine and session management for
the authentication service. It allows interaction with the database
using SQLAlchemy ORM and provides a helper function to initialize
all required tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from app.models.user import Base


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables defined in SQLAlchemy models.

    Notes:
        - Uses metadata from all imported models (e.g., User) to create tables.
        - Should be called once during application startup or migration.
    """
    Base.metadata.create_all(bind=engine)
