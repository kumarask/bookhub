"""
Pydantic schemas for the Reviews Service.

This module defines the Pydantic models used for request/response
validation and serialization throughout the Reviews Service. These
schemas ensure consistent API behavior and provide typed structures for
data exchanged between the HTTP endpoints and clients.

Currently this module provides:
    - Health: A simple schema used by the health-check endpoint to
      indicate service status.

Additional request/response schemas for reviews may be added here as
the service evolves.
"""

from pydantic import BaseModel


class Health(BaseModel):
    """
    Schema representing the health status of the service.

    Attributes:
        status (str): A human-readable string representing the
            operational status of the service (e.g., "healthy").
    """
    status: str
