"""Task completion model for tracking completed tasks in DailyQuest API.

This module defines the TaskCompletion model for recording when users
complete tasks, including XP earned and completion timestamps.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class TaskCompletion(Base):
    """TaskCompletion model for tracking when users complete tasks.
    
    Records completion events with timestamps and XP earned,
    linking to both the task and user involved.
    """
    __tablename__ = "task_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    completed_date = Column(DateTime, default=datetime.utcnow)
    xp_earned = Column(Integer, default=0)
