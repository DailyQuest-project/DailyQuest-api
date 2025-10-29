"""Task completion repository for database operations in DailyQuest API.

This module provides data access methods for task completion management
including XP calculation, streak tracking, and achievement integration.
"""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from .model import TaskCompletion
from ..task.model import Task, Habit, ToDo, Difficulty
from ..users.model import User
from ..achievements.repository import AchievementRepository


class TaskCompletionRepository:
    """Repository for task completion-related database operations and business logic."""

    def _calculate_xp_earned(self, task: Task) -> int:
        """Calcula XP baseado na dificuldade da tarefa."""
        xp_values = {
            Difficulty.EASY: 10,
            Difficulty.MEDIUM: 20,
            Difficulty.HARD: 30,
        }
        difficulty_value = Difficulty(task.difficulty)
        return xp_values.get(difficulty_value, 10)

    def calculate_xp_for_task(self, task: Task) -> int:
        """Public method for backwards compatibility with tests"""
        return self._calculate_xp_earned(task)

    def check_if_already_completed_today(
        self, db: Session, task_id: UUID, user_id: UUID
    ) -> bool:
        """Verificar se a tarefa já foi completada hoje"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        completion = (
            db.query(TaskCompletion)
            .filter(
                TaskCompletion.task_id == task_id,
                TaskCompletion.user_id == user_id,
                TaskCompletion.completed_date >= today_start,
                TaskCompletion.completed_date < today_end,
            )
            .first()
        )

        return completion is not None

    def update_habit_streak(self, db: Session, habit: Habit) -> int:
        """Atualizar streak do hábito (US#14)"""
        now = datetime.now()

        # Se nunca foi completado, streak = 1
        if habit.last_completed is None:
            setattr(habit, "current_streak", 1)
            setattr(habit, "last_completed", now)
        else:
            # Verificar se foi completado ontem (streak continua)
            yesterday = now - timedelta(days=1)
            last_completed_date = habit.last_completed.date()
            yesterday_date = yesterday.date()

            if last_completed_date == yesterday_date:
                # Streak continua
                current_streak = getattr(habit, "current_streak", 0)
                new_streak = current_streak + 1
                setattr(habit, "current_streak", new_streak)
            else:
                # Streak recomeça
                setattr(habit, "current_streak", 1)

            setattr(habit, "last_completed", now)

        db.commit()
        return getattr(habit, "current_streak", 1)

    def complete_task(
        self, db: Session, task_id: UUID, user_id: UUID
    ) -> tuple[TaskCompletion, User, bool, int]:
        """
        Completa uma tarefa e registra no histórico (US#4 e US#9).
        Atualiza XP, streak e level do usuário.
        Verifica conquistas desbloqueadas.
        """
        # 1. Buscar a task
        task = (
            db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        )
        if not task:
            raise ValueError("Task not found")

        # 2. Calcular XP earned
        xp_earned = self._calculate_xp_earned(task)

        # 3. Criar o registro de completion
        completion = TaskCompletion(
            task_id=task_id,
            user_id=user_id,
            completed_date=datetime.utcnow(),
            xp_earned=xp_earned,
        )
        db.add(completion)

        # 4. Atualizar dados do usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        current_xp = getattr(user, "xp", 0)
        new_xp = current_xp + xp_earned
        setattr(user, "xp", new_xp)

        # 5. Se for um hábito, atualizar streak
        streak_updated = False
        new_streak = 0
        if isinstance(task, Habit):
            current_streak = getattr(task, "current_streak", 0)
            new_streak = current_streak + 1
            setattr(task, "current_streak", new_streak)
            setattr(task, "last_completed", datetime.utcnow())
            streak_updated = True

        # 6. Se for um ToDo, marcar como completado
        if isinstance(task, ToDo):
            setattr(task, "completed", True)

        # 7. Verificar level up
        new_level = (new_xp // 100) + 1
        current_level = getattr(user, "level", 1)
        if new_level > current_level:
            setattr(user, "level", new_level)

        # 8. Verificar achievements
        achievement_repo = AchievementRepository()
        achievement_repo.check_and_unlock_achievements(db, user, task)

        # 9. Commit
        db.commit()
        db.refresh(completion)
        db.refresh(user)

        return completion, user, streak_updated, new_streak
