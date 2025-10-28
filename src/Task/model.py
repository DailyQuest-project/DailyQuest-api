import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Enum,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from ..database import Base

if TYPE_CHECKING:
    from sqlalchemy.sql.schema import Column as ColumnType


class Difficulty(str, PyEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class HabitFrequencyType(str, PyEnum):
    DAILY = "DAILY"
    WEEKLY_TIMES = "WEEKLY_TIMES"
    SPECIFIC_DAYS = "SPECIFIC_DAYS"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    difficulty = Column(Enum(Difficulty), nullable=False)

    task_type = Column(String(50))

    # Colunas específicas do Habit (nullable para ToDos)
    frequency_type = Column(Enum(HabitFrequencyType), nullable=True)
    frequency_target_times = Column(Integer, nullable=True)
    frequency_days_of_week = Column(Integer, nullable=True)  # Bitmask
    current_streak = Column(Integer, default=0, nullable=True)
    last_completed = Column(DateTime, nullable=True)

    # Colunas específicas do ToDo (nullable para Habits)
    deadline = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")

    __mapper_args__ = {
        "polymorphic_identity": "task",
        "polymorphic_on": task_type,
    }


class Habit(Task):
    __mapper_args__ = {"polymorphic_identity": "habit"}


class ToDo(Task):
    __mapper_args__ = {"polymorphic_identity": "todo"}
