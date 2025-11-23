"""Reviews service application package.

This package contains the Reviews service modules such as ``main``,
``db``, ``models``, ``schemas`` and ``deps``. The package-level
docstring outlines the package purpose and points to the primary entry
points for the service.

Typical contents:
- :mod:`main` - FastAPI application and HTTP endpoints for reviews.
- :mod:`db` - SQLAlchemy engine and session factory.
- :mod:`models` - ORM models representing reviews and related data.
- :mod:`schemas` - Pydantic request/response models used by endpoints.
- :mod:`deps` - dependency helpers (database session, auth placeholders).

Usage:
	Import submodules as needed::

		from . import models, db

Notes:
	Keep package-level initialization minimal and avoid heavy side
	effects at import time. Prefer performing startup tasks in
	application startup handlers (for example, :func:`main.startup`).
"""

