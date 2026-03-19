"""Authentication schemas."""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """Schema for user registration."""

    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload."""

    user_id: int
    email: str
