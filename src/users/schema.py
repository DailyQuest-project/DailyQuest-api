"""Pydantic schemas for user data validation in DailyQuest API.

This module defines the data validation schemas for user-related
operations including user creation and API responses.
"""

from typing import Optional
import uuid

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating new users with validation."""

    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        """Validate that username is not empty."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v

    @field_validator("password")
    @classmethod
    def password_must_not_be_empty(cls, v: str) -> str:
        """Validate that password is not empty."""
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class User(BaseModel):
    """Schema for user API responses including all user fields."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: EmailStr
    xp: int
    level: int
    coins: int
    avatar_url: Optional[str] = None
    theme: str
