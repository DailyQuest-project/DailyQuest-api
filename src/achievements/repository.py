"""Achievement repository for database operations in DailyQuest API.

This module provides data access methods for achievement management
including checking conditions, unlocking achievements, and listing user achievements.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from .model import UserAchievement, Achievement, AchievementKey
from ..users.model import User
from ..task.model import Task, Habit, ToDo
from ..task_completions.model import TaskCompletion


class AchievementRepository:
    """Repository for achievement-related database operations and unlock logic."""

    def list_user_achievements(
        self, db: Session, user_id: UUID
    ) -> list[UserAchievement]:
        """
        Lista todas as conquistas desbloqueadas por um usuário (US#18).
        """
        return (
            db.query(UserAchievement)
            .filter(UserAchievement.user_id == user_id)
            .options(joinedload(UserAchievement.achievement))
            .order_by(UserAchievement.unlocked_at.desc())
            .all()
        )

    def get_achievement_by_key(
        self, db: Session, key: AchievementKey
    ) -> Optional[Achievement]:
        """Busca uma definição de conquista pela sua chave interna (ex: 'LEVEL_5')."""
        return db.query(Achievement).filter(Achievement.requirement_key == key).first()

    def check_if_user_has_achievement(
        self, db: Session, user_id: UUID, achievement_id: UUID
    ) -> bool:
        """Verifica se um usuário já desbloqueou uma conquista específica."""
        return (
            db.query(UserAchievement)
            .filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
            .count()
            > 0
        )

    def unlock_achievement_for_user(
        self, db: Session, user_id: UUID, achievement: Achievement
    ) -> None:
        """
        Cria o registro de desbloqueio da conquista para o usuário.
        Verifica antes para não duplicar.
        """
        if not achievement:
            return

        # Get achievement ID as UUID value
        achievement_id = getattr(achievement, "id")
        has_achievement = self.check_if_user_has_achievement(
            db, user_id, achievement_id
        )

        if not has_achievement:
            new_unlock = UserAchievement(user_id=user_id, achievement_id=achievement_id)
            db.add(new_unlock)
            print(f"--- CONQUISTA DESBLOQUEADA: {achievement.name} ---")

    def check_first_login_achievement(self, db: Session, user_id: UUID) -> None:
        """
        Desbloqueia a conquista FIRST_LOGIN quando o usuário faz login pela primeira vez.
        """
        achievement = self.get_achievement_by_key(db, AchievementKey.FIRST_LOGIN)
        if achievement:
            self.unlock_achievement_for_user(db, user_id, achievement)
            db.commit()

    def check_and_unlock_achievements(  # pylint: disable=too-many-branches,too-many-statements
        self, db: Session, user: User, completed_task: Task
    ) -> None:
        """
        O "Motor" principal. Verifica todas as conquistas relevantes
        após a conclusão de uma tarefa.
        """
        user_id = getattr(user, "id")
        user_level = getattr(user, "level", 1)

        # 1. Verificações baseadas em Nível
        if user_level >= 5:
            achievement = self.get_achievement_by_key(db, AchievementKey.LEVEL_5)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if user_level >= 10:
            achievement = self.get_achievement_by_key(db, AchievementKey.LEVEL_10)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if user_level >= 20:
            achievement = self.get_achievement_by_key(db, AchievementKey.LEVEL_20)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if user_level >= 50:
            achievement = self.get_achievement_by_key(db, AchievementKey.LEVEL_50)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        # 2. Verificações baseadas em Tarefa
        if isinstance(completed_task, Habit):
            # Conta quantas conclusões de HÁBITOS o usuário tem
            habit_completions_count = (
                db.query(TaskCompletion.id)
                .join(Task, TaskCompletion.task_id == Task.id)
                .filter(Task.user_id == user_id, Task.task_type == "habit")
                .count()
            )

            if habit_completions_count == 1:  # Se for a primeira vez
                achievement = self.get_achievement_by_key(
                    db, AchievementKey.FIRST_HABIT
                )
                if achievement:
                    self.unlock_achievement_for_user(db, user_id, achievement)

        if isinstance(completed_task, ToDo):
            # Conta quantas conclusões de TODOs o usuário tem
            todo_completions_count = (
                db.query(TaskCompletion.id)
                .join(Task, TaskCompletion.task_id == Task.id)
                .filter(Task.user_id == user_id, Task.task_type == "todo")
                .count()
            )

            if todo_completions_count == 1:  # Se for a primeira vez
                achievement = self.get_achievement_by_key(db, AchievementKey.FIRST_TODO)
                if achievement:
                    self.unlock_achievement_for_user(db, user_id, achievement)

        # 3. Verificações baseadas em Streak
        if isinstance(completed_task, Habit):
            current_streak = getattr(completed_task, "current_streak", 0)
            if current_streak >= 3:
                achievement = self.get_achievement_by_key(db, AchievementKey.STREAK_3)
                if achievement:
                    self.unlock_achievement_for_user(db, user_id, achievement)

            if current_streak >= 7:
                achievement = self.get_achievement_by_key(db, AchievementKey.STREAK_7)
                if achievement:
                    self.unlock_achievement_for_user(db, user_id, achievement)

            if current_streak >= 30:
                achievement = self.get_achievement_by_key(db, AchievementKey.STREAK_30)
                if achievement:
                    self.unlock_achievement_for_user(db, user_id, achievement)

            if current_streak >= 100:
                achievement = self.get_achievement_by_key(db, AchievementKey.STREAK_100)
                if achievement:
                    self.unlock_achievement_for_user(db, user_id, achievement)

        # 4. Verificações baseadas em Total de Tarefas Completadas
        total_completions = db.query(TaskCompletion).filter(
            TaskCompletion.user_id == user_id
        ).count()

        if total_completions >= 10:
            achievement = self.get_achievement_by_key(db, AchievementKey.COMPLETE_10_TASKS)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if total_completions >= 50:
            achievement = self.get_achievement_by_key(db, AchievementKey.COMPLETE_50_TASKS)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if total_completions >= 100:
            achievement = self.get_achievement_by_key(db, AchievementKey.COMPLETE_100_TASKS)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if total_completions >= 500:
            achievement = self.get_achievement_by_key(db, AchievementKey.COMPLETE_500_TASKS)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        # 5. Verificação de hábitos criados (CREATE_5_HABITS)
        total_habits = db.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == "habit"
        ).count()

        if total_habits >= 5:
            achievement = self.get_achievement_by_key(db, AchievementKey.CREATE_5_HABITS)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)
