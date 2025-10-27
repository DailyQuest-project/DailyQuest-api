# Em: src/test_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.users.repository import UserRepository
from src.users.model import User
from src.utils import hash_password, verify_password


# --- Testes Unitários (Os que você já tinha) ---
class TestUserModel:
    def test_user_creation_basic(self):
        """Testa a criação do modelo User"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=hash_password("password123"),
        )
        assert user.email == "test@example.com"
        assert user.xp == 0
        assert user.level == 1

    def test_user_defaults_work(self):
        """Testa os valores padrão do modelo User"""
        user = User(
            email="defaults@test.com", username="defaultuser", password_hash="somehash"
        )
        assert user.xp == 0
        assert user.level == 1


class TestUserRepository:
    """Testes unitários para UserRepository"""

    def test_create_user_success(self, db_session: Session):
        """US#1 - Teste unitário: criar usuário com dados válidos"""
        repo = UserRepository()
        user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123",
        }

        # Mock do schema
        class MockUserCreate:
            username = user_data["username"]
            email = user_data["email"]
            password = user_data["password"]

        user = repo.create_user(db_session, MockUserCreate())

        assert (
            user.username == "newuser"
        ), f"Expected username 'newuser', got '{user.username}'"
        assert (
            user.email == "newuser@test.com"
        ), f"Expected email 'newuser@test.com', got '{user.email}'"
        assert verify_password(
            "password123", user.password_hash
        ), "Password hash verification failed"
        assert user.xp == 0, f"Expected initial XP to be 0, got {user.xp}"
        assert user.level == 1, f"Expected initial level to be 1, got {user.level}"

    def test_get_user_by_email(self, db_session: Session, test_user: User):
        """Teste unitário: buscar usuário por email"""
        repo = UserRepository()
        found_user = repo.get_user_by_email(db_session, test_user.email)

        assert found_user is not None, f"User with email '{test_user.email}' not found"
        assert (
            found_user.id == test_user.id
        ), f"Expected user ID {test_user.id}, got {found_user.id}"
        assert (
            found_user.email == test_user.email
        ), f"Expected email '{test_user.email}', got '{found_user.email}'"

    def test_get_user_by_username(self, db_session: Session, test_user: User):
        """Teste unitário: buscar usuário por username"""
        repo = UserRepository()
        found_user = repo.get_user_by_username(db_session, test_user.username)

        assert (
            found_user is not None
        ), f"User with username '{test_user.username}' not found"
        assert (
            found_user.id == test_user.id
        ), f"Expected user ID {test_user.id}, got {found_user.id}"
        assert (
            found_user.username == test_user.username
        ), f"Expected username '{test_user.username}', got '{found_user.username}'"


# --- Testes de Integração (Testando a API) ---
class TestUserAPI:
    def test_create_user_success(self, client: TestClient):
        """Testa a criação de usuário com sucesso (US#1)"""
        response = client.post(
            "/api/v1/users/",
            json={
                "username": "testapi",
                "email": "api@test.com",
                "password": "pass123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testapi"
        assert data["email"] == "api@test.com"
        assert data["xp"] == 0

    def test_create_user_duplicate_email(self, client: TestClient):
        """Testa o bloqueio de email duplicado"""
        client.post(
            "/api/v1/users/",
            json={
                "username": "user1",
                "email": "duplicate@test.com",
                "password": "pass123",
            },
        )
        # Tenta criar de novo com o mesmo email
        response = client.post(
            "/api/v1/users/",
            json={
                "username": "user2",
                "email": "duplicate@test.com",
                "password": "pass456",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_get_user_me_unauthorized(self, client: TestClient):
        """Testa se a rota /me é protegida sem token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401  # 401 Unauthorized


class TestUserEndpoints:
    """Testes de integração para endpoints de usuários"""

    def test_create_user_endpoint_success(self, client: TestClient):
        """US#1 - Teste de integração: POST /users/ com dados válidos"""
        user_data = {
            "username": "integrationuser",
            "email": "integration@test.com",
            "password": "securepass123",
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert (
            response.status_code == 201
        ), f"Expected status 201, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert (
            data["username"] == user_data["username"]
        ), f"Expected username '{user_data['username']}', got '{data['username']}'"
        assert (
            data["email"] == user_data["email"]
        ), f"Expected email '{user_data['email']}', got '{data['email']}'"
        assert data["xp"] == 0, f"Expected initial XP to be 0, got {data['xp']}"
        assert (
            data["level"] == 1
        ), f"Expected initial level to be 1, got {data['level']}"
        assert "password" not in data, "Password should not be returned in response"

    def test_create_user_duplicate_email(self, client: TestClient, test_user: User):
        """US#1 - Teste de integração: erro ao criar usuário com email duplicado"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,  # Email já existente
            "password": "password123",
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert (
            response.status_code == 400
        ), f"Expected status 400 for duplicate email, got {response.status_code}. Response: {response.text}"
        error_detail = response.json()["detail"]
        assert (
            "already registered" in error_detail
        ), f"Expected 'already registered' in error message, got: {error_detail}"

    def test_get_current_user(self, auth_client: TestClient):
        """US#5 - Teste de integração: GET /users/me usando nova fixture auth_client"""
        response = auth_client.get("/api/v1/users/me")

        assert (
            response.status_code == 200
        ), f"Expected status 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert (
            data["username"] == "testuser"
        ), f"Expected username 'testuser', got '{data['username']}'"
        assert (
            data["email"] == "test@example.com"
        ), f"Expected email 'test@example.com', got '{data['email']}'"
        assert "password" not in data, "Password should not be returned in user profile"

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Teste de integração: acesso sem autenticação"""
        response = client.get("/api/v1/users/me")

        assert (
            response.status_code == 401
        ), f"Expected status 401 for unauthorized access, got {response.status_code}. Response: {response.text}"


@pytest.mark.parametrize(
    "username,email,password,expected_status",
    [
        ("validuser", "valid@test.com", "validpass123", 201),
        ("", "valid@test.com", "validpass123", 422),  # Username vazio
        ("validuser", "invalid-email", "validpass123", 422),  # Email inválido
        ("validuser", "valid@test.com", "", 422),  # Password vazio
    ],
)
def test_create_user_validation(
    client: TestClient, username: str, email: str, password: str, expected_status: int
):
    """US#1 - Testes parametrizados: validação de dados na criação de usuários"""
    user_data = {"username": username, "email": email, "password": password}

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == expected_status, (
        f"Expected status {expected_status} for data {user_data}, "
        f"got {response.status_code}. Response: {response.text}"
    )


class TestUserIntegrationFlow:
    """Testes de fluxo completo de usuário"""

    def test_complete_user_registration_and_login_flow(self, client: TestClient):
        """US#1, US#2 - Fluxo completo: Cadastro → Login → Acesso autenticado"""
        # 1. Cadastro
        user_data = {
            "username": "flowuser",
            "email": "flow@test.com",
            "password": "flowpass123",
        }

        register_response = client.post("/api/v1/users/", json=user_data)
        assert (
            register_response.status_code == 201
        ), f"Registration failed: {register_response.text}"

        # 2. Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "flowuser", "password": "flowpass123"},
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["access_token"]
        assert token, "Access token should not be empty"

        # 3. Acesso autenticado
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert (
            profile_response.status_code == 200
        ), f"Profile access failed: {profile_response.text}"

        profile_data = profile_response.json()
        assert (
            profile_data["username"] == "flowuser"
        ), f"Expected username 'flowuser', got '{profile_data['username']}'"
        assert (
            profile_data["email"] == "flow@test.com"
        ), f"Expected email 'flow@test.com', got '{profile_data['email']}'"
