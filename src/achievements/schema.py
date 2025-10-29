"""Pydantic schemas for achievement data validation in DailyQuest API.

This module defines the data validation schemas for achievement-related
operations including achievement responses and user achievement tracking.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .model import AchievementKey


class AchievementResponse(BaseModel):
    """Schema for achievement API responses with basic achievement information."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    icon: Optional[str]
    category: str
    requirement_key: AchievementKey


class UserAchievementResponse(BaseModel):
    """Schema for user achievement API responses including unlock timestamp."""
    model_config = ConfigDict(from_attributes=True)

    unlocked_at: datetime
    achievement: AchievementResponse
