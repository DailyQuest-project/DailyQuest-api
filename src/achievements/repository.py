# Em: src/achievements/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .model import UserAchievement, Achievement, AchievementKey
from ..users.model import User
from ..Task.model import Task, Habit, ToDo
from ..task_completions.model import TaskCompletion
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Union, Optional


class AchievementRepository:

    def list_user_achievements(
        self, db: Session, user_id: UUID
    ) -> list[UserAchievement]:
        """
        Lista todas as conquistas desbloqueadas por um usuário (US#18).
        """
        return (
            db.query(UserAchievement)
            .filter(UserAchievement.user_id == user_id)
            .options(
                joinedload(UserAchievement.achievement)  # Usar o relacionamento correto
            )
            .order_by(UserAchievement.unlocked_at.desc())
            .all()
        )

    # --- NOVAS FUNÇÕES DO "MOTOR" ---

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
            return  # A conquista não existe no banco de dados

        # Get achievement ID as UUID value
        achievement_id = getattr(achievement, "id")
        has_achievement = self.check_if_user_has_achievement(
            db, user_id, achievement_id
        )

        if not has_achievement:
            new_unlock = UserAchievement(user_id=user_id, achievement_id=achievement_id)
            db.add(new_unlock)
            print(
                f"--- CONQUISTA DESBLOQUEADA: {achievement.name} ---"
            )  # Log no console

    def check_and_unlock_achievements(
        self, db: Session, user: User, completed_task: Task
    ) -> None:
        """
        O "Motor" principal. Verifica todas as conquistas relevantes
        após a conclusão de uma tarefa.
        """

        # Get user ID as UUID value
        user_id = getattr(user, "id")
        user_level = getattr(user, "level", 1)

        # 1. Verificações baseadas em Nível (ex: LEVEL_5)
        # (Nota: o usuário já foi atualizado com novo XP/Nível pelo repo anterior)
        if user_level >= 5:
            achievement = self.get_achievement_by_key(db, AchievementKey.LEVEL_5)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        if user_level >= 10:
            achievement = self.get_achievement_by_key(db, AchievementKey.LEVEL_10)
            if achievement:
                self.unlock_achievement_for_user(db, user_id, achievement)

        # 2. Verificações baseadas em Tarefa (ex: FIRST_HABIT)
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

        # 3. Verificações baseadas em Streak (ex: STREAK_3)
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
