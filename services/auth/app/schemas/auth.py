from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

# Request Schemas
class RegisterSchema(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    full_name: Optional[str]

class LoginSchema(BaseModel):
    username: str
    password: str

class RefreshTokenSchema(BaseModel):
    refresh_token: str

# Response Schemas
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserSchema(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime]


class UserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime


class ErrorResponseSchema(BaseModel):
    detail: str



class UserProfileSchema(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime


class LogoutRequestSchema(BaseModel):
    refresh_token: str

class MessageResponseSchema(BaseModel):
    message: str


class ProfileUpdateSchema(BaseModel):
    full_name: str
    email: EmailStr

class UpdatedUserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: str
    updated_at: datetime

    class Config:
        from_attributes = True