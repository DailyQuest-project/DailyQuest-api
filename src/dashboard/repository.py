# Em: src/dashboard/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from uuid import UUID
from ..task_completions.model import TaskCompletion
from ..Task.model import Habit
from ..users.model import User


class DashboardRepository:

    def get_completion_history(
        self, db: Session, user_id: UUID
    ) -> list[TaskCompletion]:
        """
        Busca o histórico de conclusões de tarefas (US#9).
        Ordena pelas mais recentes primeiro.
        """
        # Fazer join para carregar os dados da task associada
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
            db.query(func.count(TaskCompletion.id))
            .filter(TaskCompletion.user_id == user.id)
            .scalar()
        )

        # 2. Maior streak ativa
        # Esta consulta busca o hábito ativo do usuário com a maior streak
        longest_active_streak = (
            db.query(func.max(Habit.current_streak))
            .filter(Habit.user_id == user.id, Habit.is_active == True)
            .scalar()
            or 0
        )  # Retorna 0 se for None

        return {
            "total_xp": user.xp,
            "current_level": user.level,
            "total_tasks_completed": total_completions,
            "current_streak": longest_active_streak,
        }
