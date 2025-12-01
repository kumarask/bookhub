"""
Database module for SQLAlchemy setup and session management.

This module provides the SQLAlchemy engine, session factory, and base model
for defining ORM models. It also provides a dependency function `get_db`
for FastAPI routes to get a database session.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """
    Initialize the database by creating all tables defined in SQLAlchemy models.

    Notes:
        - Uses metadata from all imported models (e.g., User) to create tables.
        - Should be called once during application startup or migration.
    """
    Base.metadata.create_all(bind=engine)
