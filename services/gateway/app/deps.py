"""
Dependencies for API Gateway.

Provides helper functions for authentication and user validation
to be used as FastAPI dependencies.
"""

from fastapi import HTTPException, Depends, Request
from jose import jwt, JWTError
from app.config import JWT_SECRET_KEY


async def get_current_user(request: Request):
    """
    Validate a JWT token from the request and extract user information.

    This function is intended to be used as a FastAPI dependency
    to ensure that endpoints receive authenticated user information.

    Args:
        request (Request): FastAPI request object containing headers.

    Returns:
        dict: Decoded JWT payload representing the authenticated user.

    Raises:
        HTTPException: If the Authorization header is missing, does not start
                       with 'Bearer ', or the token is invalid.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
