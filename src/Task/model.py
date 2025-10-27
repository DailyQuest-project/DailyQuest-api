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


# Define os tipos de dificuldade
class Difficulty(str, PyEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


# --- NOVO ENUM PARA O TIPO DE FREQUÊNCIA ---
# Este Enum define o *comportamento* do hábito
class HabitFrequencyType(str, PyEnum):
    DAILY = "DAILY"  # Todo dia
    WEEKLY_TIMES = "WEEKLY_TIMES"  # X vezes por semana
    SPECIFIC_DAYS = "SPECIFIC_DAYS"  # Dias específicos (ex: Seg/Sex)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    difficulty = Column(Enum(Difficulty), nullable=False)

    # Coluna "Tipo" (Discriminador) para a Herança
    task_type = Column(String(50))

    # Relacionamento many-to-many com Tag
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")

    __mapper_args__ = {
        "polymorphic_identity": "task",
        "polymorphic_on": task_type,
    }


# --- CLASSE HABIT MODIFICADA ---
class Habit(Task):
    __tablename__ = "habits"

    id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    frequency_type = Column(Enum(HabitFrequencyType), nullable=False)

    # Campos opcionais para frequency
    frequency_days = Column(Integer, nullable=True)
    frequency_weeks = Column(Integer, nullable=True)
    frequency_target_times = Column(Integer, nullable=True)
    frequency_days_of_week = Column(Integer, nullable=True)  # Bitmask

    # Streak tracking
    current_streak = Column(Integer, default=0)
    last_completed = Column(DateTime, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "habit"}


class ToDo(Task):
    __tablename__ = "todos"

    id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    due_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)  # Used by repository
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "todo"}
