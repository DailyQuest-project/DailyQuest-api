from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from .model import AchievementKey


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    icon: Optional[str]
    category: str
    requirement_key: AchievementKey


class UserAchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unlocked_at: datetime
    achievement: AchievementResponse
