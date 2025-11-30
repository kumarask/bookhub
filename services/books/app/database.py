"""
Database configuration and session management for the application.

This module initializes the SQLAlchemy engine, session factory, and base
declarative class. It also provides a `get_db` dependency used by FastAPI
routes to create and properly close database sessions for each request.

Components:
    - engine: SQLAlchemy engine connected to the configured database.
    - SessionLocal: Factory for creating new database sessions.
    - Base: Declarative base class for defining ORM models.
    - get_db: Dependency generator that provides a scoped database session.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL  # assuming 'comfig' is intended


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Provide a database session for request handling.

    This function is used as a FastAPI dependency. It yields a database
    session for the duration of a request and ensures it is closed afterward.

    Yields:
        Session: A SQLAlchemy database session.

    Ensures:
        The session is closed after the request is completed, even if an
        exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
