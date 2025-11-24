"""
Utility functions for securely hashing and verifying passwords.

This module uses Passlib's CryptContext with bcrypt to provide secure
password hashing and comparison functions for authentication workflows.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash for a plain-text password.

    Args:
        password (str): The plain password to hash.

    Returns:
        str: A securely hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a previously hashed password.

    Args:
        plain_password (str): The user-provided plain password.
        hashed_password (str): The stored bcrypt hashed password.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
