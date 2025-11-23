"""Database helpers for the orders service.

This module centralizes the SQLAlchemy engine and session factory used
by the orders service. It exposes a configured :data:`engine` and the
``SessionLocal`` factory to obtain request-scoped sessions. Use these
objects from endpoint dependencies or repository/CRUD functions to
perform database work.

Configuration:
    ``DATABASE_URL`` is read from the environment and defaults to a
    Postgres connection string suitable for the local development
    scaffold. The engine is created with ``pool_pre_ping`` enabled to
    reduce errors from stale connections when running in containers.

Usage:
    Use :func:`init_db` at startup to create tables during development,
    and prefer a migration tool such as Alembic for production schema
    changes.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@postgres:5432/postgres"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create database tables for all registered SQLAlchemy models.

    This convenience function calls ``Base.metadata.create_all`` using the
    configured engine. It is appropriate for local development to ensure
    the database has the required tables, but production deployments
    should use a proper migration workflow instead of ``create_all``.
    """
    models.Base.metadata.create_all(bind=engine)
