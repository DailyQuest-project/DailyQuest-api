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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Movido para a classe base
    difficulty = Column(Enum(Difficulty), nullable=False)

    # Coluna "Tipo" (Discriminador) para a Herança de Tabela Única
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

    # Relacionamento many-to-many com Tag
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")

    __mapper_args__ = {
        "polymorphic_identity": "task",
        "polymorphic_on": task_type,
    }


# --- CLASSE HABIT MODIFICADA PARA HERANÇA DE TABELA ÚNICA ---
class Habit(Task):
    # Removido __tablename__ e ForeignKey para usar Herança de Tabela Única
    
    __mapper_args__ = {"polymorphic_identity": "habit"}


class ToDo(Task):
    # Removido __tablename__ e ForeignKey para usar Herança de Tabela Única
    
    __mapper_args__ = {"polymorphic_identity": "todo"}
