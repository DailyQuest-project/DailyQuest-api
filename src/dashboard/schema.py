"""Pydantic schemas for dashboard data validation in DailyQuest API.

This module defines the data validation schemas for dashboard analytics
including completion history and user statistics responses.
"""
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HistoryItem(BaseModel):
    """Schema for completion history item responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    user_id: UUID
    completed_date: datetime
    xp_earned: int


class DashboardStats(BaseModel):
    """Schema for dashboard statistics responses."""
    total_xp: int
    current_level: int
    total_tasks_completed: int
    current_streak: int


class CompletionHistory(BaseModel):
    """Schema for completion history list responses."""
    history: List[HistoryItem]
