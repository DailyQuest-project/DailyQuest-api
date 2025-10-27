from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from .model import AchievementKey


# Schema para a *definição* da conquista
class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: str
    icon: Optional[str]
    category: str
    requirement_key: AchievementKey


# Schema para a *conquista desbloqueada* pelo usuário (US#18)
class UserAchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    unlocked_at: datetime
    achievement: AchievementResponse  # Aninha os detalhes da conquista
