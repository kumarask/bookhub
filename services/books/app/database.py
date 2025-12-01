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


def init_db():
    """
    Initialize the database by creating all tables defined in SQLAlchemy models.

    Notes:
        - Uses metadata from all imported models (e.g., User) to create tables.
        - Should be called once during application startup or migration.
    """
    Base.metadata.create_all(bind=engine)
