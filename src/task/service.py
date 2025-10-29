"""Task service layer for business logic orchestration in DailyQuest API.

This module implements the TaskService class that orchestrates complex business logic
including task completion, gamification, level-up calculations, and validation rules.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from fastapi import HTTPException

from .model import Task, Habit, ToDo, Difficulty
from .repository import TaskRepository
from ..task_completions.repository import TaskCompletionRepository
from ..task_completions.model import TaskCompletion
from ..users.repository import UserRepository
from ..users.model import User
from ..achievements.repository import AchievementRepository


class TaskAlreadyCompletedError(Exception):
    """Exception raised when trying to complete an already completed task."""

    pass


class TaskNotFoundError(Exception):
    """Exception raised when task is not found or doesn't belong to user."""

    pass


class TaskService:
    """Service class for orchestrating task-related business logic.

    This service layer handles complex business rules including:
    - Task completion validation
    - XP and level-up calculations
    - Streak management
    - Achievement unlocking
    - Duplicate completion prevention
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        completion_repo: TaskCompletionRepository,
        user_repo: UserRepository,
        achievement_repo: AchievementRepository,
    ):
        """Initialize service with repository dependencies."""
        self.task_repo = task_repo
        self.completion_repo = completion_repo
        self.user_repo = user_repo
        self.achievement_repo = achievement_repo
        self.db_session: Session = None  # Will be injected by the router

    def complete_task(self, task_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Complete a task with full gamification logic.

        This is the main business logic method that:
        1. Validates task completion eligibility
        2. Executes task completion
        3. Handles XP and level progression
        4. Processes achievements
        5. Returns comprehensive completion result

        Args:
            task_id: UUID of the task to complete
            user_id: UUID of the user completing the task

        Returns:
            Dict containing completion details, XP earned, level changes, etc.

        Raises:
            TaskNotFoundError: If task doesn't exist or doesn't belong to user
            TaskAlreadyCompletedError: If task was already completed today (habits) or is already done (todos)
        """
        if not self.db_session:
            raise ValueError(
                "Database session not injected. Call set_db_session() first."
            )

        # 1. Fetch and validate entities
        task = self._get_and_validate_task(task_id, user_id)
        user = self._get_user(user_id)

        # 2. Business rule validations
        self._validate_task_completion_eligibility(task, user_id)

        # 3. Store user state before completion for comparison
        user_level_before = user.level
        user_xp_before = user.xp

        # 4. Execute core completion logic (repository persists XP, streaks, completions)
        completion, updated_user, streak_updated, new_streak = self.completion_repo.complete_task(
            db=self.db_session, task_id=task_id, user_id=user_id
        )

        # 5. Calculate level progression using the single source of truth (service)
        new_xp = getattr(updated_user, "xp", 0)
        new_level = self.calculate_level_from_xp(new_xp)
        current_level = user_level_before
        if new_level > current_level:
            # Persist level change
            setattr(updated_user, "level", new_level)
            # Commit the level update so subsequent achievement checks see it
            self.db_session.commit()
            self.db_session.refresh(updated_user)
            level_up_occurred = True
            levels_gained = new_level - current_level
        else:
            level_up_occurred = False
            levels_gained = 0

        # 6. Process achievements now that user's XP/level are up-to-date
        # Use the injected achievement repository
        try:
            self.achievement_repo.check_and_unlock_achievements(self.db_session, updated_user, task)
            # Ensure unlocked achievements are persisted
            self.db_session.commit()
        except Exception:
            # If achievements check fails, we don't want to break the completion flow
            # but we also don't want to hide errors silently in production.
            # Re-raise to let higher layers handle or log accordingly.
            raise

        # 7. Prepare comprehensive response
        return self._build_completion_response(
            completion=completion,
            updated_user=updated_user,
            streak_updated=streak_updated,
            new_streak=new_streak,
            level_up_occurred=level_up_occurred,
            levels_gained=levels_gained,
            user_xp_before=user_xp_before,
            user_level_before=user_level_before,
            task=task,
        )

    def set_db_session(self, db_session: Session):
        """Set the database session for all repositories."""
        self.db_session = db_session

    def _get_and_validate_task(self, task_id: UUID, user_id: UUID) -> Task:
        """Get task and validate ownership."""
        task = self.task_repo.get_task_by_id(
            db=self.db_session, task_id=task_id, user_id=user_id
        )
        if not task:
            raise TaskNotFoundError(
                f"Task {task_id} not found or doesn't belong to user"
            )
        return task

    def _get_user(self, user_id: UUID) -> User:
        """Get user by ID."""
        user = self.user_repo.get_user_by_id(db=self.db_session, user_id=user_id)
        if not user:
            raise TaskNotFoundError(f"User {user_id} not found")
        return user

    def _validate_task_completion_eligibility(self, task: Task, user_id: UUID) -> None:
        """Validate if task can be completed based on business rules."""

        # Rule 1: ToDos cannot be completed if already marked as completed
        if isinstance(task, ToDo) and task.completed:
            raise TaskAlreadyCompletedError(
                "This ToDo has already been completed and cannot be completed again"
            )

        # Rule 2: Habits cannot be completed multiple times on the same day
        if isinstance(task, Habit):
            if self.completion_repo.check_if_already_completed_today(
                db=self.db_session, task_id=task.id, user_id=user_id
            ):
                raise TaskAlreadyCompletedError(
                    "This habit has already been completed today. Try again tomorrow!"
                )

    def _build_completion_response(
        self,
        completion: TaskCompletion,
        updated_user: User,
        streak_updated: bool,
        new_streak: int,
        level_up_occurred: bool,
        levels_gained: int,
        user_xp_before: int,
        user_level_before: int,
        task: Task,
    ) -> Dict[str, Any]:
        """Build comprehensive completion response with all relevant data."""

        # Base completion message
        message_parts = [f"Task completed! XP earned: {completion.xp_earned}"]

        # Add streak information for habits
        if isinstance(task, Habit) and streak_updated:
            message_parts.append(f"Current streak: {new_streak} days!")

        # Add level-up information
        if level_up_occurred:
            if levels_gained == 1:
                message_parts.append(
                    f"🎉 Level up! You reached level {updated_user.level}!"
                )
            else:
                message_parts.append(
                    f"🎉 Multiple level ups! You jumped {levels_gained} levels to level {updated_user.level}!"
                )

        return {
            "message": " ".join(message_parts),
            "task_completion": completion,
            "user": updated_user,
            "streak_updated": streak_updated,
            "new_streak": new_streak,
            "gamification": {
                "xp_earned": completion.xp_earned,
                "xp_before": user_xp_before,
                "xp_after": updated_user.xp,
                "level_before": user_level_before,
                "level_after": updated_user.level,
                "level_up_occurred": level_up_occurred,
                "levels_gained": levels_gained,
            },
            "task_info": {
                "task_id": task.id,
                "task_type": (
                    task.task_type
                    if hasattr(task, "task_type")
                    else type(task).__name__.lower()
                ),
                "task_title": task.title,
                "difficulty": (
                    task.difficulty.value
                    if isinstance(task.difficulty, Difficulty)
                    else task.difficulty
                ),
            },
        }

    def calculate_level_from_xp(self, xp: int) -> int:
        """Calculate user level from XP amount.

        Business rule: Every 100 XP = 1 level, starting at level 1.
        """
        return (xp // 100) + 1

    def calculate_xp_needed_for_next_level(self, current_xp: int) -> int:
        """Calculate XP needed to reach the next level."""
        current_level = self.calculate_level_from_xp(current_xp)
        xp_for_next_level = current_level * 100
        return xp_for_next_level - current_xp

    def validate_habit_frequency_completion(self, habit: Habit) -> bool:
        """Validate if habit can be completed based on its frequency settings.

        This is a placeholder for more complex frequency validation logic.
        Currently, the basic daily completion check is handled elsewhere.
        """
        # Future enhancement: Handle WEEKLY_TIMES, SPECIFIC_DAYS frequency types
        # For now, return True as basic validation is handled in _validate_task_completion_eligibility
        return True
