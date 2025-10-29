"""Pydantic schemas for task data validation in DailyQuest API.

This module defines the data validation schemas for task-related
operations including habits and todos creation, updates, and API responses.
"""
from datetime import datetime, date
from typing import Optional, List, Union
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, ConfigDict

from .model import HabitFrequencyType, Difficulty


# Base schemas
class TaskBase(BaseModel):
    """Base schema for task data with common fields."""
    title: str
    description: Optional[str] = None
    difficulty: Difficulty = Difficulty.EASY


class HabitCreate(BaseModel):
    """Schema for creating new habits with frequency settings."""
    title: str
    description: Optional[str] = None
    difficulty: Difficulty = Difficulty.EASY

    frequency_type: HabitFrequencyType = HabitFrequencyType.DAILY

    frequency_target_times: Optional[int] = Field(None, gt=0, lt=8)

    # Lista de dias da semana (0=Segunda, 6=Domingo) - apenas para SPECIFIC_DAYS
    frequency_days: Optional[List[int]] = Field(None, max_length=7)


class HabitResponse(TaskBase):
    """Schema for habit API responses including computed fields."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    task_type: str = "habit"
    current_streak: int = 0
    best_streak: int = 0
    last_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    frequency_type: HabitFrequencyType
    frequency_target_times: Optional[int] = None
    frequency_days_of_week: Optional[int] = None  # Bitmask salvo no banco

    @computed_field
    @property
    def frequency_days(self) -> Optional[List[int]]:
        """Converte o bitmask do banco para lista de dias para a API"""
        if self.frequency_days_of_week is None:
            return None

        days: List[int] = []
        for i in range(7):
            if self.frequency_days_of_week & (1 << i):
                days.append(i)
        return days


class ToDoCreate(TaskBase):
    """Schema for creating new todos with optional deadlines."""
    deadline: Optional[date] = None


class ToDoResponse(TaskBase):
    """Schema for todo API responses including completion status."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    task_type: str = "todo"
    deadline: Optional[date] = None
    completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


TaskResponse = Union[HabitResponse, ToDoResponse]
