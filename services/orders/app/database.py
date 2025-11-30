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


def get_db():
    """
    Provides a database session for dependency injection.

    This function yields a SQLAlchemy session that can be used in FastAPI
    route handlers. The session is automatically closed after use.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
