"""
Database utilities for the reviews service.

This module centralizes database setup and session management for the
reviews service. It provides:

- Creation of the SQLAlchemy engine using the configured `DATABASE_URL`.
- A `SessionLocal` factory for producing database sessions with
  controlled commit/flush behavior.
- A helper function (`init_db`) that initializes all database tables
  defined in the application's SQLAlchemy models.

Environment Variables:
    DATABASE_URL (str): Optional. A SQLAlchemy-compatible database URL.
        Defaults to a local PostgreSQL instance if not provided.

The module interacts with the rest of the application through the
configured SQLAlchemy engine and session factory. It should be imported
wherever database sessions or schema initialization are required.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/postgres"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initialize the database schema.

    Creates all tables defined by the SQLAlchemy models in the current
    metadata. This function is typically executed during application
    startup or migrations to ensure the database schema is up to date.

    Returns:
        None

    Raises:
        sqlalchemy.exc.SQLAlchemyError: If table creation fails.
    """
    models.Base.metadata.create_all(bind=engine)
