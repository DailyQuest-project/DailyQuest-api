"""Dashboard repository for analytics and statistics in DailyQuest API.

This module provides data access methods for dashboard analytics,
completion history, and user statistics.
"""
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..task_completions.model import TaskCompletion
from ..task.model import Habit
from ..users.model import User


class DashboardRepository:
    """Repository for dashboard-related database operations."""

    def get_completion_history(
        self, db: Session, user_id: UUID
    ) -> list[TaskCompletion]:
        """
        Busca o histórico de conclusões de tarefas (US#9).
        Ordena pelas mais recentes primeiro.
        """
        return (
            db.query(TaskCompletion)
            .filter(TaskCompletion.user_id == user_id)
            .order_by(desc(TaskCompletion.completed_date))
            .all()
        )

    def get_dashboard_stats(self, db: Session, user: User) -> dict:
        """
        Calcula as estatísticas para o dashboard (US#19).
        """
        # 1. Total de tarefas completadas
        total_completions = (
            db.query(TaskCompletion)
            .filter(TaskCompletion.user_id == user.id)
            .count()
        )

        # 2. Maior streak ativa
        # Esta consulta busca o hábito ativo do usuário com a maior streak
        longest_active_streak = (
            db.query(func.max(Habit.current_streak))
            .filter(Habit.user_id == user.id, Habit.is_active.is_(True))
            .scalar()
            or 0
        )

        return {
            "total_xp": user.xp,
            "current_level": user.level,
            "total_tasks_completed": total_completions,
            "current_streak": longest_active_streak,
        }
