"""Task functionality tests for DailyQuest API.

This module contains unit and integration tests for task management
including habits and todos CRUD operations, validation, and tag integration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.task.repository import TaskRepository
from src.task.model import Habit, ToDo, Difficulty, HabitFrequencyType
from src.task.schema import HabitCreate, ToDoCreate
from src.users.model import User
from src.tags.model import Tag


def _convert_days_list_to_bitmask(days_list):
    """Converte uma lista de dias da semana em bitmask"""
    bitmask = 0
    for day in days_list:
        bitmask |= 1 << day
    return bitmask


# --- Teste Unitário e Parametrizado---
@pytest.mark.parametrize(
    "days_list, expected_bitmask",
    [
        ([0, 4], 17),  # Seg/Sex
        ([1, 2, 3], 14),  # Ter/Qua/Qui
        ([], 0),
    ],
)
def test_bitmask_conversion(days_list, expected_bitmask):
    """Testa a lógica de conversão do bitmask."""
    assert _convert_days_list_to_bitmask(days_list) == expected_bitmask


# --- Testes de Integração ---
class TestTaskAPI:
    """Integration tests for task API endpoints with authentication."""

    @pytest.fixture(autouse=True)
    def auth_client(self, client: TestClient) -> TestClient:
        """
        Uma fixture que cria um usuário, loga, e retorna o
        cliente com o token de autorização já configurado.
        """
        client.post(
            "/api/v1/users/",
            json={
                "username": "task_user",
                "email": "task@test.com",
                "password": "pass123",
            },
        )
        login_response = client.post(
            "/api/v1/auth/login", data={"username": "task_user", "password": "pass123"}
        )
        token = login_response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        return client

    def test_create_habit_and_todo(self, auth_client: TestClient):
        """Testa a criação de um hábito (US#3) e um ToDo (US#8)"""
        # Cria Hábito
        response_habit = auth_client.post(
            "/api/v1/tasks/habits/",
            json={
                "title": "Ler 10 páginas",
                "difficulty": "EASY",
                "frequency_type": "DAILY",
            },
        )
        assert response_habit.status_code == 201
        assert response_habit.json()["task_type"] == "habit"

        # Cria ToDo
        response_todo = auth_client.post(
            "/api/v1/tasks/todos/",
            json={
                "title": "Entregar o projeto",
                "difficulty": "HARD",
                "deadline": "2025-11-30",
            },
        )
        assert response_todo.status_code == 201
        assert response_todo.json()["task_type"] == "todo"

    def test_list_all_tasks(self, auth_client: TestClient):
        """Testa a listagem de todas as tarefas (US#6)"""
        auth_client.post(
            "/api/v1/tasks/habits/",
            json={"title": "Hábito 1", "difficulty": "EASY", "frequency_type": "DAILY"},
        )
        auth_client.post(
            "/api/v1/tasks/todos/",
            json={"title": "ToDo 1", "difficulty": "MEDIUM", "deadline": "2025-11-01"},
        )

        response = auth_client.get("/api/v1/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Hábito 1"
        assert data[1]["title"] == "ToDo 1"


class TestTaskRepository:
    """Unit tests for TaskRepository database operations."""

    def test_create_habit_success(self, db_session: Session, test_user: User):
        """US#3 - Teste unitário: criar hábito"""
        repo = TaskRepository()

        habit_schema = HabitCreate(
            title="Test Habit",
            description="Test description",
            difficulty=Difficulty.MEDIUM,
            frequency_type=HabitFrequencyType.DAILY,
            frequency_target_times=None,
            frequency_days=None,
        )

        habit = repo.create_habit(db_session, habit_schema, test_user.id)

        assert habit.title == "Test Habit"
        assert habit.difficulty == Difficulty.MEDIUM
        assert habit.frequency_type == HabitFrequencyType.DAILY
        assert habit.user_id == test_user.id

    def test_create_todo_success(self, db_session: Session, test_user: User):
        """US#8 - Teste unitário: criar todo"""
        repo = TaskRepository()

        todo_schema = ToDoCreate(
            title="Test Todo",
            description="Test todo description",
            difficulty=Difficulty.HARD,
            deadline=None,
        )

        todo = repo.create_todo(db_session, todo_schema, test_user.id)

        assert todo.title == "Test Todo"
        assert todo.difficulty == Difficulty.HARD
        assert todo.user_id == test_user.id
        assert todo.completed is False

    def test_get_tasks_by_user(
        self, db_session: Session, test_user: User, test_habit: Habit, test_todo: ToDo
    ):
        """US#6 - Teste unitário: listar tarefas do usuário"""
        repo = TaskRepository()
        tasks = repo.get_tasks_by_user(db_session, test_user.id)

        assert len(tasks) == 2
        task_titles = [task.title for task in tasks]
        assert "Test Habit" in task_titles
        assert "Test Todo" in task_titles

    def test_update_habit(
        self, db_session: Session, test_user: User, test_habit: Habit
    ):
        """US#10 - Teste unitário: atualizar hábito"""
        repo = TaskRepository()

        update_schema = HabitCreate(
            title="Updated Habit",
            description="Updated description",
            difficulty=Difficulty.HARD,
            frequency_type=HabitFrequencyType.WEEKLY_TIMES,
            frequency_target_times=3,
            frequency_days=None,
        )

        updated_habit = repo.update_habit(
            db_session, test_habit.id, test_user.id, update_schema
        )

        assert updated_habit.title == "Updated Habit"
        assert updated_habit.difficulty == Difficulty.HARD
        assert updated_habit.frequency_type == HabitFrequencyType.WEEKLY_TIMES
        assert updated_habit.frequency_target_times == 3

    def test_delete_habit(
        self, db_session: Session, test_user: User, test_habit: Habit
    ):
        """US#10 - Teste unitário: deletar hábito"""
        repo = TaskRepository()
        result = repo.delete_habit(db_session, test_habit.id, test_user.id)

        assert result is True

        deleted_habit = repo.get_task_by_id(db_session, test_habit.id, test_user.id)
        assert deleted_habit is None


class TestTaskEndpoints:
    """Integration tests for task REST API endpoints."""

    def test_create_habit_endpoint(self, client: TestClient, auth_headers: dict):
        """US#3 - Teste de integração: POST /tasks/habits/"""
        habit_data = {
            "title": "Morning Exercise",
            "description": "Daily morning workout",
            "difficulty": "EASY",
            "frequency_type": "DAILY",
        }

        response = client.post(
            "/api/v1/tasks/habits/", json=habit_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Morning Exercise"
        assert data["difficulty"] == "EASY"
        assert data["frequency_type"] == "DAILY"
        assert data["current_streak"] == 0

    def test_create_todo_endpoint(self, client: TestClient, auth_headers: dict):
        """US#8 - Teste de integração: POST /tasks/todos/"""
        todo_data = {
            "title": "Buy groceries",
            "description": "Weekly grocery shopping",
            "difficulty": "MEDIUM",
        }

        response = client.post(
            "/api/v1/tasks/todos/", json=todo_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["difficulty"] == "MEDIUM"
        assert data["completed"] is False

    def test_get_user_tasks(
        self, client: TestClient, auth_headers: dict, test_habit: Habit, test_todo: ToDo
    ):
        """US#6 - Teste de integração: GET /tasks/"""
        response = client.get("/api/v1/tasks/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        task_types = [task["task_type"] for task in data]
        assert "habit" in task_types
        assert "todo" in task_types

    def test_update_habit_endpoint(
        self, client: TestClient, auth_headers: dict, test_habit: Habit
    ):
        """US#10 - Teste de integração: PUT /tasks/habits/{id}"""
        update_data = {
            "title": "Updated Morning Exercise",
            "description": "Updated workout routine",
            "difficulty": "HARD",
            "frequency_type": "WEEKLY_TIMES",
            "frequency_target_times": 5,
        }

        response = client.put(
            f"/api/v1/tasks/habits/{test_habit.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Morning Exercise"
        assert data["difficulty"] == "HARD"
        assert data["frequency_target_times"] == 5

    def test_delete_habit_endpoint(
        self, client: TestClient, auth_headers: dict, test_habit: Habit
    ):
        """US#10 - Teste de integração: DELETE /tasks/habits/{id}"""
        response = client.delete(
            f"/api/v1/tasks/habits/{test_habit.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_unauthorized_access(self, client: TestClient):
        """Teste: acesso não autorizado aos endpoints de tarefas"""
        responses = [
            client.get("/api/v1/tasks/"),
            client.post("/api/v1/tasks/habits/", json={"title": "Test"}),
            client.post("/api/v1/tasks/todos/", json={"title": "Test"}),
        ]

        for response in responses:
            assert response.status_code == 401


@pytest.mark.parametrize(
    "difficulty,frequency_type,expected_status",
    [
        ("EASY", "DAILY", 201),
        ("MEDIUM", "WEEKLY_TIMES", 201),
        ("HARD", "SPECIFIC_DAYS", 201),
        ("INVALID", "DAILY", 422),  # Dificuldade inválida
        ("EASY", "INVALID", 422),  # Frequência inválida
    ],
)
def test_create_habit_validation(
    client: TestClient,
    auth_headers: dict,
    difficulty: str,
    frequency_type: str,
    expected_status: int,
):
    """US#3, US#11 - Testes parametrizados: validação na criação de hábitos"""
    habit_data = {
        "title": "Test Habit",
        "difficulty": difficulty,
        "frequency_type": frequency_type,
    }

    response = client.post(
        "/api/v1/tasks/habits/", json=habit_data, headers=auth_headers
    )
    assert response.status_code == expected_status


class TestTaskTagIntegration:
    """Integration tests for task and tag associations."""

    def test_add_tag_to_task(
        self, client: TestClient, auth_headers: dict, test_habit: Habit, test_tag: Tag
    ):
        """US#12 - Teste: associar tag a tarefa"""
        response = client.post(
            f"/api/v1/tasks/{test_habit.id}/tags/{test_tag.id}", headers=auth_headers
        )

        assert response.status_code == 200
        # Verificar se a tag foi associada na resposta
        # (dependendo da implementação do response model)

    def test_remove_tag_from_task(
        self, client: TestClient, auth_headers: dict, test_habit: Habit, test_tag: Tag
    ):
        """US#12 - Teste: desassociar tag de tarefa"""
        # Primeiro associar
        client.post(
            f"/api/v1/tasks/{test_habit.id}/tags/{test_tag.id}", headers=auth_headers
        )

        # Depois desassociar
        response = client.delete(
            f"/api/v1/tasks/{test_habit.id}/tags/{test_tag.id}", headers=auth_headers
        )

        assert response.status_code == 200

    def test_filter_tasks_by_tag(
        self, client: TestClient, auth_headers: dict, test_tag: Tag
    ):
        """US#12 - Teste: filtrar tarefas por tag"""
        response = client.get(
            f"/api/v1/tasks/by-tag/{test_tag.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTaskFlow:
    """Complete workflow tests for task management."""

    def test_complete_habit_management_flow(
        self, client: TestClient, auth_headers: dict
    ):
        """US#3, US#6, US#10 - Fluxo: Criar → Listar → Atualizar → Deletar hábito"""
        # 1. Criar hábito
        create_response = client.post(
            "/api/v1/tasks/habits/",
            json={
                "title": "Flow Habit",
                "difficulty": "MEDIUM",
                "frequency_type": "DAILY",
            },
            headers=auth_headers,
        )

        assert create_response.status_code == 201
        habit_id = create_response.json()["id"]

        # 2. Listar e verificar se aparece
        list_response = client.get("/api/v1/tasks/", headers=auth_headers)
        assert list_response.status_code == 200
        habits = [task for task in list_response.json() if task["task_type"] == "habit"]
        assert len(habits) >= 1

        # 3. Atualizar
        update_response = client.put(
            f"/api/v1/tasks/habits/{habit_id}",
            json={
                "title": "Updated Flow Habit",
                "difficulty": "HARD",
                "frequency_type": "WEEKLY_TIMES",
                "frequency_target_times": 3,
            },
            headers=auth_headers,
        )

        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Flow Habit"

        # 4. Deletar
        delete_response = client.delete(
            f"/api/v1/tasks/habits/{habit_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200
