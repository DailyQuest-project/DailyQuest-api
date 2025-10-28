from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
from ..users.schema import User


class TaskCompletionCreate(BaseModel):
    """Schema para criar um TaskCompletion"""

    pass


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
