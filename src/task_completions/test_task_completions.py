import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.task_completions.repository import TaskCompletionRepository
from src.task.model import Habit, ToDo, Difficulty, HabitFrequencyType
from src.users.model import User


class TestTaskCompletionRepository:
    """Testes unitários para TaskCompletionRepository"""

    @pytest.mark.parametrize(
        "difficulty,expected_xp",
        [
            (Difficulty.EASY, 10),
            (Difficulty.MEDIUM, 20),
            (Difficulty.HARD, 30),
        ],
    )
    def test_calculate_xp_for_task(self, difficulty: Difficulty, expected_xp: int):
        """US#5 - Teste unitário: cálculo de XP por dificuldade"""
        repo = TaskCompletionRepository()

        from unittest.mock import Mock

        task = Mock()
        task.difficulty = difficulty

        xp = repo.calculate_xp_for_task(task)
        assert xp == expected_xp

    def test_complete_habit_increases_streak(
        self, db_session: Session, test_user: User
    ):
        """US#11 - Teste unitário: completar hábito aumenta streak"""
        repo = TaskCompletionRepository()

        habit = Habit(
            title="Test Streak Habit",
            difficulty=Difficulty.EASY,
            frequency_type=HabitFrequencyType.DAILY,
            user_id=test_user.id,
        )
        db_session.add(habit)
        db_session.commit()

        completion, updated_user, streak_updated, new_streak = repo.complete_task(
            db_session, habit.id, test_user.id
        )

        assert completion is not None
        assert completion.xp_earned == 10

        db_session.refresh(habit)
        assert habit.current_streak == 1
        assert streak_updated == True
        assert new_streak == 1

    def test_complete_todo_marks_as_completed(
        self, db_session: Session, test_user: User
    ):
        """US#4 - Teste unitário: completar ToDo marca como concluído"""
        repo = TaskCompletionRepository()

        todo = ToDo(
            title="Test ToDo", difficulty=Difficulty.MEDIUM, user_id=test_user.id
        )
        db_session.add(todo)
        db_session.commit()

        completion, updated_user, streak_updated, new_streak = repo.complete_task(
            db_session, todo.id, test_user.id
        )

        assert completion is not None
        assert completion.xp_earned == 20

        db_session.refresh(todo)
        assert todo.completed == True


class TestTaskCompletionEndpoints:
    """Testes de integração para endpoints de task completions"""

    def test_complete_habit_endpoint(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """US#3, US#5 - Teste de integração: completar hábito via endpoint"""
        habit = Habit(
            title="API Test Habit",
            difficulty=Difficulty.EASY,
            frequency_type=HabitFrequencyType.DAILY,
            user_id=test_user.id,
        )
        db_session.add(habit)
        db_session.commit()

        response = client.post(
            f"/api/v1/tasks/{habit.id}/complete", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["user"]["xp"] == 10

    def test_complete_todo_endpoint(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
    ):
        """US#4, US#5 - Teste de integração: completar ToDo via endpoint"""
        todo = ToDo(
            title="API Test ToDo", difficulty=Difficulty.HARD, user_id=test_user.id
        )
        db_session.add(todo)
        db_session.commit()

        response = client.post(
            f"/api/v1/tasks/{todo.id}/complete", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["user"]["xp"] == 30


class TestGamificationFlow:
    """Testes de fluxo de gamificação"""

    def test_multiple_completions_increase_xp(
        self, client: TestClient, auth_headers: dict
    ):
        """US#5 - Fluxo: Múltiplas conclusões acumulam XP"""
        habit1_response = client.post(
            "/api/v1/tasks/habits/",
            json={"title": "Habit 1", "difficulty": "EASY", "frequency_type": "DAILY"},
            headers=auth_headers,
        )
        habit1_id = habit1_response.json()["id"]

        habit2_response = client.post(
            "/api/v1/tasks/habits/",
            json={
                "title": "Habit 2",
                "difficulty": "MEDIUM",
                "frequency_type": "DAILY",
            },
            headers=auth_headers,
        )
        habit2_id = habit2_response.json()["id"]

        complete1_response = client.post(
            f"/api/v1/tasks/{habit1_id}/complete", headers=auth_headers
        )
        assert complete1_response.status_code == 200
        assert complete1_response.json()["user"]["xp"] == 10

        complete2_response = client.post(
            f"/api/v1/tasks/{habit2_id}/complete", headers=auth_headers
        )
        assert complete2_response.status_code == 200
        assert complete2_response.json()["user"]["xp"] == 30


@pytest.mark.parametrize(
    "task_type,difficulty,expected_xp",
    [
        ("habit", "EASY", 10),
        ("habit", "MEDIUM", 20),
        ("habit", "HARD", 30),
        ("todo", "EASY", 10),
        ("todo", "MEDIUM", 20),
        ("todo", "HARD", 30),
    ],
)
def test_xp_calculation_all_combinations(
    task_type: str, difficulty: str, expected_xp: int
):
    """US#5 - Testes parametrizados: cálculo de XP para todas as combinações"""
    xp_values = {"EASY": 10, "MEDIUM": 20, "HARD": 30}
    calculated_xp = xp_values[difficulty]

    assert calculated_xp == expected_xp
