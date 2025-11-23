"""Pydantic request/response schemas for the orders service.

This module defines lightweight Pydantic models used to validate and
serialize request and response payloads for the Orders service API.
The scaffold currently includes a minimal ``Health`` schema; as the
service evolves add models such as ``OrderCreate``, ``OrderRead``, and
``OrderItem`` to improve validation and OpenAPI documentation.

Examples:
    Use these in route declarations::

        @app.get("/health", response_model=Health)
        def health():
            return {"status": "healthy"}
"""

from pydantic import BaseModel


class Health(BaseModel):
    """Health check response schema.

    Attributes:
        status (str): service health text, typically ``"healthy"``.
    """
    status: str
