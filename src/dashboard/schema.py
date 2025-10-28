# Em: src/dashboard/schema.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from uuid import UUID
from typing import List


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    user_id: UUID
    completed_date: datetime
    xp_earned: int


class DashboardStats(BaseModel):
    total_xp: int
    current_level: int
    total_tasks_completed: int
    current_streak: int


class CompletionHistoryResponse(BaseModel):
    history: List[HistoryItem]
    total_days: int
    total_tasks_completed: int
    total_xp_earned: int
