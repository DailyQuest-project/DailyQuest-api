"""Pydantic schemas for task completion data validation in DailyQuest API.

This module defines the data validation schemas for task completion operations
including completion tracking, XP calculation, and check-in responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ..users.schema import User


class TaskCompletionCreate(BaseModel):
    """Schema para criar um TaskCompletion"""

    # No fields needed for creation as all data comes from the task and user context


class TaskCompletionResponse(BaseModel):
    """Schema para resposta de TaskCompletion"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    user_id: UUID
    completed_date: datetime
    xp_earned: int


class CheckInResponse(BaseModel):
    """Schema para resposta do check-in"""

    message: str
    task_completion: TaskCompletionResponse
    user: Optional[User] = None
    streak_updated: bool = False
    new_streak: int = 0
