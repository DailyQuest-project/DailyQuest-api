"""Task repository for database operations in DailyQuest API.

This module provides data access methods for task management
including habits and todos CRUD operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import model, schema
from ..tags.model import Tag
from ..task_completions.model import TaskCompletion


def _convert_days_list_to_bitmask(days: List[int]) -> int:
    """Converte uma lista de dias [0, 4] para um bitmask (17)."""
    bitmask = 0
    for day_index in days:
        if 0 <= day_index <= 6:
            bitmask |= 1 << day_index  # (1 << 0) é 1, (1 << 4) é 16
    return bitmask


def _convert_bitmask_to_days_list(bitmask: int) -> List[int]:
    """Converte um bitmask (17) para uma lista de dias [0, 4]."""
    days = []
    for i in range(7):
        if bitmask & (1 << i):
            days.append(i)
    return days


class TaskRepository:
    """Repository for task-related database operations."""

    def create_habit(
        self, db: Session, habit: schema.HabitCreate, user_id: UUID
    ) -> model.Habit:
        """Create a new habit for a user."""
        bitmask_days = None
        if (
            habit.frequency_type == model.HabitFrequencyType.SPECIFIC_DAYS
            and habit.frequency_days
        ):
            bitmask_days = _convert_days_list_to_bitmask(habit.frequency_days)

        db_habit = model.Habit(
            title=habit.title,
            description=habit.description,
            difficulty=habit.difficulty,
            user_id=user_id,
            frequency_type=habit.frequency_type,
            frequency_target_times=habit.frequency_target_times,
            frequency_days_of_week=bitmask_days,
        )

        # Adicionar tags se fornecidas
        if habit.tag_ids:
            tags = db.query(Tag).filter(
                Tag.id.in_(habit.tag_ids),
                Tag.user_id == user_id
            ).all()
            db_habit.tags = tags

        db.add(db_habit)
        db.commit()
        db.refresh(db_habit)
        return db_habit

    def create_todo(
        self, db: Session, todo: schema.ToDoCreate, user_id: UUID
    ) -> model.ToDo:
        """Criar uma nova tarefa ToDo"""
        db_todo = model.ToDo(
            user_id=user_id,
            title=todo.title,
            description=todo.description,
            difficulty=todo.difficulty,
            deadline=todo.deadline,
        )
        
        # Adicionar tags se fornecidas
        if todo.tag_ids:
            tags = db.query(Tag).filter(
                Tag.id.in_(todo.tag_ids),
                Tag.user_id == user_id
            ).all()
            db_todo.tags = tags
        
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def get_tasks_by_user(self, db: Session, user_id: UUID) -> list[model.Task]:
        """Buscar todas as tarefas (hábitos e todos) de um usuário"""
        return db.query(model.Task).filter(model.Task.user_id == user_id).all()

    def get_task_by_id(
        self, db: Session, task_id: UUID, user_id: UUID
    ) -> Optional[model.Task]:
        """Buscar uma tarefa específica por ID e usuário"""
        return (
            db.query(model.Task)
            .filter(model.Task.id == task_id, model.Task.user_id == user_id)
            .first()
        )

    def update_habit(
        self,
        db: Session,
        habit_id: UUID,
        user_id: UUID,
        habit_update: schema.HabitCreate,
    ) -> Optional[model.Habit]:
        """Atualizar um hábito existente"""
        db_habit = (
            db.query(model.Task)
            .filter(
                model.Task.id == habit_id,
                model.Task.user_id == user_id,
                model.Task.task_type == "habit",
            )
            .first()
        )

        if db_habit:
            bitmask_days = None
            if (
                habit_update.frequency_type == model.HabitFrequencyType.SPECIFIC_DAYS
                and habit_update.frequency_days
            ):
                bitmask_days = _convert_days_list_to_bitmask(
                    habit_update.frequency_days
                )

            db_habit.title = habit_update.title
            db_habit.description = habit_update.description or ""
            db_habit.difficulty = habit_update.difficulty
            db_habit.frequency_type = habit_update.frequency_type
            db_habit.frequency_target_times = habit_update.frequency_target_times
            db_habit.frequency_days_of_week = bitmask_days
            db_habit.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(db_habit)

        return db_habit

    def delete_habit(self, db: Session, habit_id: UUID, user_id: UUID) -> bool:
        """Deletar um hábito"""
        db_habit = (
            db.query(model.Task)
            .filter(
                model.Task.id == habit_id,
                model.Task.user_id == user_id,
                model.Task.task_type == "habit",
            )
            .first()
        )

        if db_habit:
            db.query(TaskCompletion).filter(TaskCompletion.task_id == habit_id).delete(
                synchronize_session=False
            )

            db.delete(db_habit)
            db.commit()
            return True

        return False

    def add_tag_to_task(self, db: Session, task: model.Task, tag: Tag) -> model.Task:
        """Associa uma tag a uma tarefa."""
        if tag not in task.tags:
            task.tags.append(tag)
            db.commit()
            db.refresh(task)
        return task

    def remove_tag_from_task(
        self, db: Session, task: model.Task, tag: Tag
    ) -> model.Task:
        """Desassocia uma tag de uma tarefa."""
        if tag in task.tags:
            task.tags.remove(tag)
            db.commit()
            db.refresh(task)
        return task

    def get_tasks_by_tag(
        self, db: Session, user_id: UUID, tag_id: UUID
    ) -> List[model.Task]:
        """
        Retorna todas as tarefas de um usuário que estão associadas a uma tag específica.
        """
        return (
            db.query(model.Task)
            .filter(
                model.Task.user_id == user_id,
                model.Task.tags.any(id=tag_id),
            )
            .all()
        )

    def update_todo(
        self,
        db: Session,
        todo_id: UUID,
        user_id: UUID,
        todo_update: "schema.ToDoUpdate",
    ) -> Optional[model.ToDo]:
        """Atualizar um ToDo existente"""
        db_todo = (
            db.query(model.Task)
            .filter(
                model.Task.id == todo_id,
                model.Task.user_id == user_id,
                model.Task.task_type == "todo",
            )
            .first()
        )

        if db_todo:
            # Atualiza apenas campos fornecidos
            if todo_update.title is not None:
                db_todo.title = todo_update.title
            if todo_update.description is not None:
                db_todo.description = todo_update.description
            if todo_update.difficulty is not None:
                db_todo.difficulty = todo_update.difficulty
            if getattr(todo_update, "deadline", None) is not None:
                db_todo.deadline = todo_update.deadline

            db_todo.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_todo)

        return db_todo

    def delete_todo(self, db: Session, todo_id: UUID, user_id: UUID) -> bool:
        """Deletar um ToDo"""
        db_todo = (
            db.query(model.Task)
            .filter(
                model.Task.id == todo_id,
                model.Task.user_id == user_id,
                model.Task.task_type == "todo",
            )
            .first()
        )

        if db_todo:
            # Remover completions relacionadas antes de apagar a task
            db.query(TaskCompletion).filter(TaskCompletion.task_id == todo_id).delete(
                synchronize_session=False
            )

            db.delete(db_todo)
            db.commit()
            return True

        return False
