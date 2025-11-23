"""
User API Module

This module provides endpoints for managing and retrieving user data in the system.
It is built using FastAPI and SQLAlchemy.

Endpoints:
-----------
GET /api/v1/user/
    - Description: List all users in the system.
    - Response: List of user objects with fields:
        - id (str): User ID
        - email (str): User email
        - username (str): Username
        - full_name (str): Full name of the user
        - is_active (bool): Indicates if the user account is active

GET /api/v1/user/{user_id}
    - Description: Retrieve a single user by their unique ID.
    - Path Parameters:
        - user_id (str): The ID of the user to retrieve
    - Response: User object with fields:
        - id (str): User ID
        - email (str): User email
        - username (str): Username
        - full_name (str): Full name of the user
        - is_active (bool): Indicates if the user account is active
    - Error Responses:
        - 404: User not found
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.user import User

router = APIRouter(prefix="/api/v1/user", tags=["user"])

@router.get("/", response_model=list[dict])
def list_users(db: Session = Depends(get_db)):
    """
    List all users.

    Retrieves a list of all users from the database.

    Args:
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: A list of user objects. Each object contains:
            - id (str): User ID
            - email (str): User email
            - username (str): Username
            - full_name (str): Full name of the user
            - is_active (bool): Whether the user account is active
    """
    users = db.query(User).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "is_active": u.is_active,
        }
        for u in users
    ]


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get a user by ID.

    Retrieves a single user from the database using their unique ID.

    Args:
        user_id (str): The unique identifier of the user.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the user with the given ID does not exist (status code 404).

    Returns:
        dict: A dictionary representing the user object with the following fields:
            - id (str): User ID
            - email (str): User email
            - username (str): Username
            - full_name (str): Full name of the user
            - is_active (bool): Whether the user account is active
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }
