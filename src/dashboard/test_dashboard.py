"""Tests for dashboard functionality in DailyQuest API.

This module contains tests for dashboard repository and endpoints,
including completion history and user statistics.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.dashboard.repository import DashboardRepository
from src.users.model import User
from src.task.model import Habit
from src.task_completions.model import TaskCompletion


class TestDashboardRepository:
    """Testes unitários para DashboardRepository"""

    def test_get_completion_history_empty(self, db_session: Session, test_user: User):
        """US#9 - Teste unitário: histórico vazio"""
        repo = DashboardRepository()
        history = repo.get_completion_history(db_session, test_user.id)

        assert history == []

    def test_get_completion_history_with_data(
        self, db_session: Session, test_user: User, test_habit: Habit
    ):
        """US#9 - Teste unitário: histórico com dados"""
        # Criar completion
        completion = TaskCompletion(
            task_id=test_habit.id, user_id=test_user.id, xp_earned=10
        )
        db_session.add(completion)
        db_session.commit()

        repo = DashboardRepository()
        history = repo.get_completion_history(db_session, test_user.id)

        assert len(history) == 1
        assert history[0].xp_earned == 10
        assert history[0].task_id == test_habit.id

    def test_get_dashboard_stats(
        self, db_session: Session, test_user: User, test_habit: Habit
    ):
        """US#19 - Teste unitário: estatísticas do dashboard"""
        # Configurar dados de teste
        test_user.xp = 150
        test_user.level = 3
        test_habit.current_streak = 5
        test_habit.is_active = True

        # Criar completion
        completion = TaskCompletion(
            task_id=test_habit.id, user_id=test_user.id, xp_earned=20
        )
        db_session.add(completion)
        db_session.commit()

        repo = DashboardRepository()
        stats = repo.get_dashboard_stats(db_session, test_user)

        assert stats["total_xp"] == 150
        assert stats["current_level"] == 3
        assert stats["total_tasks_completed"] == 1
        assert stats["current_streak"] == 5


class TestDashboardEndpoints:
    """Testes de integração para endpoints do dashboard"""

    def test_get_user_history_empty(self, client: TestClient, auth_headers: dict):
        """US#9 - Teste de integração: histórico vazio"""
        response = client.get("/api/v1/dashboard/history", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_user_history_with_completions(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_user: User,
        test_habit: Habit,
    ):
        """US#9 - Teste de integração: histórico com completions"""
        # Criar alguns completions
        for i in range(3):
            completion = TaskCompletion(
                task_id=test_habit.id, user_id=test_user.id, xp_earned=10 + i
            )
            db_session.add(completion)
        db_session.commit()

        response = client.get("/api/v1/dashboard/history", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verificar se está ordenado por data (mais recente primeiro)
        xp_values = [item["xp_earned"] for item in data]
        assert xp_values == [12, 11, 10]  # Ordem decrescente

    def test_get_user_dashboard(self, client: TestClient, auth_headers: dict):
        """US#19 - Teste de integração: dashboard estatísticas"""
        response = client.get("/api/v1/dashboard/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura da resposta
        required_fields = [
            "total_xp",
            "current_level",
            "total_tasks_completed",
            "current_streak",
        ]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], int)

    def test_dashboard_unauthorized(self, client: TestClient):
        """Teste de integração: acesso sem autenticação"""
        response = client.get("/api/v1/dashboard/")

        assert response.status_code == 403


class TestDashboardFlow:
    """Testes de fluxo completo do dashboard"""

    def test_complete_dashboard_flow(self, client: TestClient, auth_headers: dict):
        """US#9, US#19 - Fluxo: Criar → Completar → Verificar dashboard → Verificar histórico"""
        # 1. Criar hábito
        habit_response = client.post(
            "/api/v1/tasks/habits/",
            json={
                "title": "Dashboard Test Habit",
                "difficulty": "MEDIUM",
                "frequency_type": "DAILY",
            },
            headers=auth_headers,
        )

        habit_id = habit_response.json()["id"]

        # 2. Completar hábito
        complete_response = client.post(
            f"/api/v1/tasks/{habit_id}/complete", headers=auth_headers
        )
        assert complete_response.status_code == 200

        # 3. Verificar dashboard atualizado
        dashboard_response = client.get("/api/v1/dashboard/", headers=auth_headers)
        assert dashboard_response.status_code == 200

        dashboard_data = dashboard_response.json()
        assert dashboard_data["total_xp"] == 20  # MEDIUM = 20 XP
        assert dashboard_data["total_tasks_completed"] == 1
        assert dashboard_data["current_streak"] == 1

        # 4. Verificar histórico
        history_response = client.get("/api/v1/dashboard/history", headers=auth_headers)
        assert history_response.status_code == 200

        history_data = history_response.json()
        assert len(history_data) == 1
        assert history_data[0]["xp_earned"] == 20


@pytest.mark.parametrize(
    "num_completions,expected_total",
    [
        (0, 0),
        (1, 10),
        (3, 30),
        (5, 50),
    ],
)
def test_dashboard_stats_parametrized(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    client: TestClient,
    auth_headers: dict,
    db_session: Session,
    test_user: User,
    test_habit: Habit,
    num_completions: int,
    expected_total: int,
):
    """US#19 - Testes parametrizados: dashboard com diferentes quantidades de completions"""
    # Criar completions
    for _ in range(num_completions):
        completion = TaskCompletion(
            task_id=test_habit.id, user_id=test_user.id, xp_earned=10
        )
        db_session.add(completion)

    # Atualizar XP do usuário
    test_user.xp = expected_total
    db_session.commit()

    response = client.get("/api/v1/dashboard/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks_completed"] == num_completions
    assert data["total_xp"] == expected_total
