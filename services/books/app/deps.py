"""
Internal service authentication utilities.

This module provides a security helper used to validate internal service
requests by checking a custom header against a predefined internal secret.
It is intended for internal microservice-to-microservice communication
where an extra layer of trust validation is required.

Functions:
    - verify_internal_secret: Ensures the request contains the correct
      internal service secret header.
"""

from fastapi import Header, HTTPException
from app.config import INTERNAL_SECRET


def verify_internal_secret(x_internal_secret: str = Header(...)):
    """
    Validate the internal service secret header.

    This function verifies that the incoming request contains the correct
    internal secret value. It is typically used as a FastAPI dependency to
    secure internal endpoints that should only be accessed by trusted services.

    Args:
        x_internal_secret (str): The value of the `X-Internal-Secret` header.

    Returns:
        bool: True if the secret is valid.

    Raises:
        HTTPException: If the provided secret does not match the expected value.
    """
    if x_internal_secret != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Invalid internal service secret")
    return True
