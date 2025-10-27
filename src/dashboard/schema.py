# Em: src/dashboard/schema.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from uuid import UUID
from typing import List


# Schema para um item individual do histórico (US#9)
class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    user_id: UUID
    completed_date: datetime
    xp_earned: int


# Schema para as estatísticas do dashboard (US#19)
class DashboardStats(BaseModel):
    total_xp: int
    current_level: int
    total_tasks_completed: int
    current_streak: int  # A maior sequência ativa do usuário


class CompletionHistoryResponse(BaseModel):
    history: List[HistoryItem]
    total_days: int
    total_tasks_completed: int
    total_xp_earned: int
