"""
Auth API routes (v1) for the Auth Service.

This module provides FastAPI endpoints for user authentication and profile management, including:

- User registration
- Login & JWT token management
- Refreshing access tokens
- Fetching current user profile
- Updating user profile
- Logout & refresh token invalidation

Redis caching is used for user profile data. Pub/Sub events are published for user registration and updates.
"""

import json
import uuid
import datetime
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, get_redis
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.security.hashing import get_password_hash
from app.schemas.auth import (
    RegisterSchema,
    TokenSchema,
    ProfileUpdateSchema,
    UserResponseSchema,
    UpdatedUserResponseSchema,
    ErrorResponseSchema,
    RefreshTokenSchema,
    MessageResponseSchema,
    LogoutRequestSchema,
)
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.services.token_service import blacklist_token
from app.pubsub import publish

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponseSchema,
            "description": "Email or username already exists",
        },
        422: {"model": ErrorResponseSchema, "description": "Validation error"},
    },
)
def register(payload: RegisterSchema, db: Session = Depends(get_db)):
    """
    Register a new user.

    Checks if the email or username already exists, hashes the password,
    stores the user in the database, caches profile data, and publishes
    a `user.registered` event.

    Args:
        payload (RegisterSchema): Registration request payload.
        db (Session, optional): Database session.

    Returns:
        UserResponseSchema: Newly created user information.

    Raises:
        HTTPException: 400 if email or username already exists.
    """
    if (
        db.query(User)
        .filter((User.email == payload.email) | (User.username == payload.username))
        .first()
    ):
        raise HTTPException(status_code=400, detail="Email or username already exists")

    new_user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
        is_admin=False,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    asyncio.create_task(
        publish("user.registered", {"user_id": new_user.id, "email": new_user.email})
    )

    return UserResponseSchema(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
    )


@router.post(
    "/login",
    response_model=TokenSchema,
    responses={
        401: {"model": ErrorResponseSchema, "description": "Invalid credentials"},
        403: {"model": ErrorResponseSchema, "description": "Account inactive"},
    },
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and issue access & refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): Username and password form data.
        db (Session, optional): Database session.

    Returns:
        TokenSchema: Access and refresh tokens with type and expiry.

    Raises:
        HTTPException: 401 if invalid credentials, 403 if account inactive.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account inactive")

    access_token = create_access_token(str(user.id))
    refresh_token_str = create_refresh_token()

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
    )
    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": 3600,
    }


@router.post(
    "/refresh",
    response_model=TokenSchema,
    responses={
        401: {
            "model": ErrorResponseSchema,
            "description": "Invalid or expired refresh token",
        },
        422: {"model": ErrorResponseSchema, "description": "Validation error"},
    },
)
def refresh_token(payload: RefreshTokenSchema, db: Session = Depends(get_db)):
    """
    Refresh an access token using a valid refresh token.

    Args:
        payload (RefreshTokenSchema): Contains the refresh token string.
        db (Session, optional): Database session.

    Returns:
        TokenSchema: New access token with type and expiry.

    Raises:
        HTTPException: 401 if refresh token is invalid or expired.
    """
    user_id = verify_refresh_token(payload.refresh_token, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = create_access_token(user_id)
    return TokenSchema(access_token=access_token, token_type="bearer", expires_in=3600)


@router.get(
    "/me",
    response_model=UserResponseSchema,
    responses={401: {"description": "Unauthorized"}},
)
def get_me(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the currently authenticated user's profile.

    Uses Redis caching to improve performance.

    Args:
        db (Session, optional): Database session.
        redis: Redis client dependency.
        current_user (User): Authenticated user object.

    Returns:
        UserResponseSchema: User profile information.

    Raises:
        HTTPException: 401 if token is invalid or expired.
    """
    cache_key = f"user:{current_user.id}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat(),
    }

    redis.set(cache_key, json.dumps(user_data), ex=3600)
    return user_data


@router.post(
    "/logout",
    response_model=MessageResponseSchema,
    responses={401: {"description": "Unauthorized"}},
)
def logout(
    body: LogoutRequestSchema,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Logout a user by invalidating the provided refresh token.

    Args:
        body (LogoutRequestSchema): Refresh token to invalidate.
        token (str): Access token from Authorization header.
        db (Session, optional): Database session.

    Returns:
        MessageResponseSchema: Success message.

    Raises:
        HTTPException: 401 if access token is invalid or refresh token expired.
    """
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=401, detail="Unauthorized (invalid/expired token)"
        )

    if not verify_refresh_token(body.refresh_token, db):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    blacklist_token(body.refresh_token, db)
    return {"message": "Successfully logged out"}


@router.put("/profile", response_model=UpdatedUserResponseSchema)
def update_profile(
    payload: ProfileUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis=Depends(get_redis),
):
    """
    Update the currently authenticated user's profile.

    Updates full name and email, caches updated profile in Redis,
    and publishes a `user.updated` event.

    Args:
        payload (ProfileUpdateSchema): Updated profile information.
        db (Session, optional): Database session.
        current_user (User): Authenticated user object.
        redis: Redis client dependency.

    Returns:
        UpdatedUserResponseSchema: Updated user profile.

    Raises:
        HTTPException: 400 if email is already taken by another user.
    """
    if (
        db.query(User)
        .filter(User.email == payload.email, User.id != current_user.id)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Email already exists")

    current_user.full_name = payload.full_name
    current_user.email = payload.email
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    asyncio.create_task(
        publish(
            "user.updated", {"user_id": current_user.id, "email": current_user.email}
        )
    )

    redis.set(
        f"user:{current_user.id}",
        json.dumps(
            {
                "id": str(current_user.id),
                "email": current_user.email,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "is_active": current_user.is_active,
                "is_admin": current_user.is_admin,
                "created_at": current_user.created_at.isoformat(),
            }
        ),
        ex=3600,
    )

    return current_user
