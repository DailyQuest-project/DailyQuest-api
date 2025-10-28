# Em: src/achievements/model.py
import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.database import Base
from datetime import datetime
from enum import Enum as PyEnum
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..users.model import User


class AchievementKey(str, PyEnum):
    LEVEL_5 = "LEVEL_5"
    LEVEL_10 = "LEVEL_10"
    FIRST_HABIT = "FIRST_HABIT"
    FIRST_TODO = "FIRST_TODO"
    STREAK_3 = "STREAK_3_DAYS"
    STREAK_7 = "STREAK_7_DAYS"


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    requirement_key = Column(Enum(AchievementKey), nullable=False)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False
    )
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento: Permite acessar os detalhes da conquista
    achievement = relationship("Achievement", lazy="joined")
