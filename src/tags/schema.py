"""Pydantic schemas for tag data validation in DailyQuest API.

This module defines the data validation schemas for tag-related
operations including creation, updates, and API responses.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, ConfigDict


class TagBase(BaseModel):
    """Base schema for tag data with common fields."""
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    """Schema for creating new tags with validation."""

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that tag name is not empty."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v


class TagResponse(TagBase):
    """Schema for tag API responses including database fields."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID


class TagUpdate(BaseModel):
    """Schema for updating existing tags with optional fields."""
    name: Optional[str] = None
    color: Optional[str] = None
