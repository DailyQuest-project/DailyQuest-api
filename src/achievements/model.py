"""Achievement models for gamification features in DailyQuest API.

This module defines the Achievement and UserAchievement models for tracking
user progress and unlocking rewards based on various criteria.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base

if TYPE_CHECKING:
    from ..users.model import User


class AchievementKey(str, PyEnum):
    """Enumeration of achievement requirement keys for unlocking conditions."""
    LEVEL_5 = "LEVEL_5"
    LEVEL_10 = "LEVEL_10"
    FIRST_HABIT = "FIRST_HABIT"
    FIRST_TODO = "FIRST_TODO"
    STREAK_3 = "STREAK_3_DAYS"
    STREAK_7 = "STREAK_7_DAYS"


class Achievement(Base):
    """Achievement model for defining unlockable rewards and milestones.
    
    Stores achievement definitions including name, description, icon,
    category, and the requirement key that determines unlock conditions.
    """
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    requirement_key = Column(Enum(AchievementKey), nullable=False)


class UserAchievement(Base):
    """UserAchievement model for tracking unlocked achievements per user.
    
    Links users to their unlocked achievements with timestamps,
    creating a many-to-many relationship between users and achievements.
    """
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False
    )
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento: Permite acessar os detalhes da conquista
    achievement = relationship("Achievement", lazy="joined")
