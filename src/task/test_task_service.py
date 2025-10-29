"""Integration tests for TaskService business logic layer.

This module contains real integration tests for the TaskService class,
testing business logic with real database operations and dependencies.
"""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from src.task.service import TaskService, TaskAlreadyCompletedError, TaskNotFoundError
from src.task.model import Habit, ToDo, Difficulty, HabitFrequencyType
from src.task.repository import TaskRepository
from src.task_completions.repository import TaskCompletionRepository
from src.users.repository import UserRepository
from src.users.model import User
from src.achievements.repository import AchievementRepository
from src.utils import hash_password


class TestTaskServiceIntegration:
    """Integration tests for TaskService with real database operations."""

    @pytest.fixture
    def task_service(self, db_session):
        """Create TaskService instance with real repositories and inject DB session."""
        service = TaskService(
            task_repo=TaskRepository(),
            completion_repo=TaskCompletionRepository(),
            user_repo=UserRepository(),
            achievement_repo=AchievementRepository(),
        )
        # Inject database session using the new method
        service.set_db_session(db_session)
        return service

    @pytest.fixture
    def real_user(self, db_session):
        """Create a real user for integration tests."""
        user = User(
            username="integrationuser",
            email="integration@test.com",
            password_hash=hash_password("password123"),
            xp=50,
            level=1,
            coins=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def real_habit(self, db_session, real_user):
        """Create a real habit for integration tests."""
        habit = Habit(
            title="Integration Habit",
            description="Real habit for testing",
            user_id=real_user.id,
            difficulty=Difficulty.MEDIUM,
            frequency_type=HabitFrequencyType.DAILY,
            current_streak=0,
        )
        db_session.add(habit)
        db_session.commit()
        db_session.refresh(habit)
        return habit

    @pytest.fixture
    def real_todo(self, db_session, real_user):
        """Create a real todo for integration tests."""
        todo = ToDo(
            title="Integration Todo",
            description="Real todo for testing",
            user_id=real_user.id,
            difficulty=Difficulty.HARD,
            completed=False,
        )
        db_session.add(todo)
        db_session.commit()
        db_session.refresh(todo)
        return todo

    def test_complete_habit_success_real_data(
        self, task_service, db_session, real_user, real_habit
    ):
        """Test successful habit completion with real database operations."""
        # Act
        result = task_service.complete_task(real_habit.id, real_user.id)

        # Assert - Verify response structure
        assert result is not None
        assert "message" in result
        assert "task_completion" in result
        assert "user" in result
        assert "gamification" in result

        # Verify XP was earned (MEDIUM difficulty = 20 XP)
        assert result["gamification"]["xp_earned"] == 20
        assert result["gamification"]["xp_before"] == 50
        assert result["gamification"]["xp_after"] == 70

        # Verify streak was updated
        assert result["streak_updated"] is True
        assert result["new_streak"] == 1

        # Verify message contains completion info
        assert "Task completed!" in result["message"]
        assert "XP earned: 20" in result["message"]
        assert "Current streak: 1 days!" in result["message"]

        # Verify database state was updated
        db_session.refresh(real_habit)
        db_session.refresh(real_user)
        assert real_habit.current_streak == 1
        assert real_user.xp == 70

    def test_complete_todo_success_real_data(
        self, task_service, db_session, real_user, real_todo
    ):
        """Test successful todo completion with real database operations."""
        # Act
        result = task_service.complete_task(real_todo.id, real_user.id)

        # Assert
        assert result["gamification"]["xp_earned"] == 30  # HARD difficulty
        assert result["gamification"]["xp_before"] == 50
        assert result["gamification"]["xp_after"] == 80
        assert result["streak_updated"] is False  # Todos don't have streaks

        # Verify database state - todo should be marked as completed
        db_session.refresh(real_todo)
        db_session.refresh(real_user)
        assert real_todo.completed is True
        assert real_user.xp == 80

    def test_prevent_duplicate_habit_completion_real_data(
        self, task_service, db_session, real_user, real_habit
    ):
        """Test that habits cannot be completed multiple times on the same day."""
        # Complete habit first time
        result1 = task_service.complete_task(real_habit.id, real_user.id)
        assert result1 is not None

        # Try to complete again - should raise exception
        with pytest.raises(TaskAlreadyCompletedError) as exc_info:
            task_service.complete_task(real_habit.id, real_user.id)

        assert "already been completed today" in str(exc_info.value)

    def test_prevent_duplicate_todo_completion_real_data(
        self, task_service, db_session, real_user, real_todo
    ):
        """Test that completed todos cannot be completed again."""
        # Complete todo first time
        result1 = task_service.complete_task(real_todo.id, real_user.id)
        assert result1 is not None

        # Verify todo is marked as completed
        db_session.refresh(real_todo)
        assert real_todo.completed is True

        # Try to complete again - should raise exception
        with pytest.raises(TaskAlreadyCompletedError) as exc_info:
            task_service.complete_task(real_todo.id, real_user.id)

        assert "already been completed" in str(exc_info.value)

    def test_level_up_calculation_real_data(self, task_service, db_session, real_user):
        """Test level up calculation with real user progression."""
        # Set user close to level up (90 XP = almost level 2)
        real_user.xp = 90
        real_user.level = 1
        db_session.commit()

        # Create a habit that will give enough XP to level up
        habit = Habit(
            title="Level Up Habit",
            description="Habit for level up test",
            user_id=real_user.id,
            difficulty=Difficulty.MEDIUM,  # 20 XP
            frequency_type=HabitFrequencyType.DAILY,
        )
        db_session.add(habit)
        db_session.commit()

        # Complete habit - should trigger level up
        result = task_service.complete_task(habit.id, real_user.id)

        # Assert level up occurred
        assert result["gamification"]["level_up_occurred"] is True
        assert result["gamification"]["levels_gained"] == 1
        assert result["gamification"]["level_before"] == 1
        assert result["gamification"]["level_after"] == 2
        assert "🎉 Level up! You reached level 2!" in result["message"]

        # Verify database state
        db_session.refresh(real_user)
        assert real_user.level == 2
        assert real_user.xp == 110

    def test_multiple_level_up_real_data(self, task_service, db_session, real_user):
        """Test multiple level ups with massive XP gain."""
        # Set user at low level
        real_user.xp = 50
        real_user.level = 1
        db_session.commit()

        # Complete multiple tasks to gain lots of XP
        total_xp_gained = 0

        for i in range(10):  # 10 HARD tasks = 300 XP
            todo = ToDo(
                title=f"Bulk Todo {i}",
                description="Todo for bulk testing",
                user_id=real_user.id,
                difficulty=Difficulty.HARD,  # 30 XP each
            )
            db_session.add(todo)
            db_session.commit()

            result = task_service.complete_task(todo.id, real_user.id)
            total_xp_gained += result["gamification"]["xp_earned"]

        # Final user should have jumped multiple levels
        db_session.refresh(real_user)
        final_xp = 50 + total_xp_gained  # 50 initial + 300 gained = 350 XP
        expected_level = (final_xp // 100) + 1  # Level 4

        assert real_user.xp == final_xp
        assert real_user.level == expected_level

    def test_task_not_found_error_real_data(self, task_service, real_user):
        """Test TaskNotFoundError with non-existent task."""
        fake_task_id = uuid4()

        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.complete_task(fake_task_id, real_user.id)

        assert "not found" in str(exc_info.value)

    def test_user_not_found_error_real_data(self, task_service, real_habit):
        """Test TaskNotFoundError with non-existent user."""
        fake_user_id = uuid4()

        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.complete_task(real_habit.id, fake_user_id)

        # The error message should indicate that the task was not found (because user doesn't exist)
        # The task repository filters by both task_id AND user_id, so if user doesn't exist,
        # the task won't be found for that user
        assert "not found" in str(exc_info.value)

    @pytest.mark.parametrize(
        "xp,expected_level",
        [
            (0, 1),  # 0 XP = Level 1
            (50, 1),  # 50 XP = Level 1
            (99, 1),  # 99 XP = Level 1
            (100, 2),  # 100 XP = Level 2
            (150, 2),  # 150 XP = Level 2
            (199, 2),  # 199 XP = Level 2
            (200, 3),  # 200 XP = Level 3
            (1000, 11),  # 1000 XP = Level 11
        ],
    )
    def test_calculate_level_from_xp_business_logic(
        self, task_service, xp, expected_level
    ):
        """Test level calculation business logic with various XP amounts."""
        assert task_service.calculate_level_from_xp(xp) == expected_level

    @pytest.mark.parametrize(
        "current_xp,expected_xp_needed",
        [
            (0, 100),  # At 0 XP, need 100 more for level 2
            (50, 50),  # At 50 XP, need 50 more for level 2
            (99, 1),  # At 99 XP, need 1 more for level 2
            (100, 100),  # At 100 XP (level 2), need 100 more for level 3
            (150, 50),  # At 150 XP (level 2), need 50 more for level 3
            (200, 100),  # At 200 XP (level 3), need 100 more for level 4
        ],
    )
    def test_calculate_xp_for_next_level_business_logic(
        self, task_service, current_xp, expected_xp_needed
    ):
        """Test XP calculation for next level with various current XP amounts."""
        assert (
            task_service.calculate_xp_needed_for_next_level(current_xp)
            == expected_xp_needed
        )

    def test_comprehensive_workflow_real_data(
        self, task_service, db_session, real_user
    ):
        """Test complete workflow: create tasks, complete them, verify all side effects."""
        # Create multiple tasks
        habit = Habit(
            title="Workflow Habit",
            user_id=real_user.id,
            difficulty=Difficulty.EASY,  # 10 XP
            frequency_type=HabitFrequencyType.DAILY,
        )
        todo = ToDo(
            title="Workflow Todo",
            user_id=real_user.id,
            difficulty=Difficulty.MEDIUM,  # 20 XP
        )
        db_session.add_all([habit, todo])
        db_session.commit()

        initial_xp = real_user.xp

        # Complete habit
        habit_result = task_service.complete_task(habit.id, real_user.id)
        assert habit_result["gamification"]["xp_earned"] == 10

        # Complete todo
        todo_result = task_service.complete_task(todo.id, real_user.id)
        assert todo_result["gamification"]["xp_earned"] == 20

        # Verify final state
        db_session.refresh(real_user)
        db_session.refresh(habit)
        db_session.refresh(todo)

        assert real_user.xp == initial_xp + 30  # 10 + 20 XP gained
        assert habit.current_streak == 1
        assert todo.completed is True
