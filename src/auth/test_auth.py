"""Authentication endpoint tests for DailyQuest API.

This module contains integration tests for user authentication,
login functionality, and token-based access control.
"""

import pytest
from fastapi.testclient import TestClient
from src.users.model import User


class TestAuthEndpoints:
    """Testes de integração para autenticação"""

    def test_login_success(self, client: TestClient, test_user: User):
        """US#2 - Teste de integração: login com credenciais válidas"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_username(self, client: TestClient):
        """US#2 - Teste: login com username inexistente"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "password123"},
        )

        assert response.status_code == 401
        assert "Nome de usuário ou senha incorretos" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """US#2 - Teste: login com senha incorreta"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Nome de usuário ou senha incorretos" in response.json()["detail"]

    def test_login_missing_credentials(self, client: TestClient):
        """US#2 - Teste: login sem credenciais"""
        response = client.post("/api/v1/auth/login", data={})

        assert response.status_code == 422  # Validation error


@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("testuser", "testpass123", 200),  # Válido
        ("testuser", "wrongpass", 401),  # Senha errada
        ("wronguser", "testpass123", 401),  # Username errado
        ("", "testpass123", 422),  # Username vazio
        ("testuser", "", 422),  # Password vazio
    ],
)
def test_login_parametrized(
    client: TestClient,
    test_user: User,
    username: str,
    password: str,
    expected_status: int,
):
    """US#2 - Testes parametrizados: diferentes cenários de login"""
    response = client.post(
        "/api/v1/auth/login", data={"username": username, "password": password}
    )

    assert response.status_code == expected_status


class TestAuthFlow:
    """Testes de fluxo de autenticação"""

    def test_token_access_flow(self, client: TestClient, test_user: User):
        """US#2 - Fluxo completo: Login → Usar token → Acessar recurso protegido"""
        # 1. Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Usar token para acessar recurso protegido
        headers = {"Authorization": f"Bearer {token}"}
        protected_response = client.get("/api/v1/users/me", headers=headers)

        assert protected_response.status_code == 200
        user_data = protected_response.json()
        assert user_data["username"] == "testuser"

    def test_invalid_token_access(self, client: TestClient):
        """Teste: acesso com token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401

    def test_malformed_token_header(self, client: TestClient):
        """Teste: header de autorização mal formado"""
        headers = {"Authorization": "invalid_format"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
