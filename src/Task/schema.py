# Em: src/tasks/schema.py
from pydantic import BaseModel, Field, computed_field, ConfigDict
from typing import Optional, List, Union
from datetime import datetime, date
from uuid import UUID
from .model import HabitFrequencyType, Difficulty


# Base schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: Difficulty = Difficulty.EASY


class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: Difficulty = Difficulty.EASY

    frequency_type: HabitFrequencyType = HabitFrequencyType.DAILY

    frequency_target_times: Optional[int] = Field(None, gt=0, lt=8)

    # Lista de dias da semana (0=Segunda, 6=Domingo) - apenas para SPECIFIC_DAYS
    frequency_days: Optional[List[int]] = Field(None, max_length=7)


class HabitResponse(TaskBase):
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
    deadline: Optional[date] = None


class ToDoResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    task_type: str = "todo"
    deadline: Optional[date] = None
    completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


TaskResponse = Union[HabitResponse, ToDoResponse]
