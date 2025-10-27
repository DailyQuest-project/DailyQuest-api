import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.tags.repository import TagRepository
from src.tags.model import Tag
from src.users.model import User


class TestTagRepository:
    """Testes unitários para TagRepository"""

    def test_create_tag_success(self, db_session: Session, test_user: User):
        """US#7 - Teste unitário: criar tag"""
        repo = TagRepository()
        class MockTagCreate:
            name = "Work"
            color = "#FF0000"

        tag = repo.create_tag(db_session, MockTagCreate(), test_user.id)

        assert tag.name == "Work"
        assert tag.color == "#FF0000"
        assert tag.user_id == test_user.id

    def test_get_tags_by_user(
        self, db_session: Session, test_user: User, test_tag: Tag
    ):
        """US#7 - Teste unitário: listar tags do usuário"""
        repo = TagRepository()
        tags = repo.get_tags_by_user(db_session, test_user.id)

        assert len(tags) == 1
        assert tags[0].name == "Test Tag"
        assert tags[0].user_id == test_user.id

    def test_update_tag(self, db_session: Session, test_user: User, test_tag: Tag):
        """US#7 - Teste unitário: atualizar tag"""
        repo = TagRepository()

        # Mock do schema de update
        class MockTagUpdate:
            name = "Updated Tag"
            color = "#00FF00"

        updated_tag = repo.update_tag(
            db_session, test_tag.id, test_user.id, MockTagUpdate()
        )

        assert updated_tag.name == "Updated Tag"
        assert updated_tag.color == "#00FF00"

    def test_delete_tag(self, db_session: Session, test_user: User, test_tag: Tag):
        """US#7 - Teste unitário: deletar tag"""
        repo = TagRepository()
        result = repo.delete_tag(db_session, test_tag.id, test_user.id)

        assert result is True

        # Verificar se foi realmente deletada
        deleted_tag = repo.get_tag_by_id(db_session, test_tag.id, test_user.id)
        assert deleted_tag is None


class TestTagEndpoints:
    """Testes de integração para endpoints de tags"""

    def test_create_tag_endpoint(self, client: TestClient, auth_headers: dict):
        """US#7 - Teste de integração: POST /tags/"""
        tag_data = {"name": "Personal", "color": "#0000FF"}

        response = client.post("/api/v1/tags/", json=tag_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Personal"
        assert data["color"] == "#0000FF"

    def test_get_user_tags(self, client: TestClient, auth_headers: dict):
        """US#7 - Teste de integração: GET /tags/"""
        # Criar algumas tags primeiro
        client.post(
            "/api/v1/tags/",
            json={"name": "Work", "color": "#FF0000"},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/tags/",
            json={"name": "Personal", "color": "#00FF00"},
            headers=auth_headers,
        )

        response = client.get("/api/v1/tags/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        tag_names = [tag["name"] for tag in data]
        assert "Work" in tag_names
        assert "Personal" in tag_names

    def test_get_specific_tag(
        self, client: TestClient, auth_headers: dict, test_tag: Tag
    ):
        """US#7 - Teste de integração: GET /tags/{id}"""
        response = client.get(f"/api/v1/tags/{test_tag.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Tag"
        assert data["color"] == "#FF0000"

    def test_update_tag_endpoint(
        self, client: TestClient, auth_headers: dict, test_tag: Tag
    ):
        """US#7 - Teste de integração: PUT /tags/{id}"""
        update_data = {"name": "Updated Test Tag", "color": "#FFFF00"}

        response = client.put(
            f"/api/v1/tags/{test_tag.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Test Tag"
        assert data["color"] == "#FFFF00"

    def test_delete_tag_endpoint(
        self, client: TestClient, auth_headers: dict, test_tag: Tag
    ):
        """US#7 - Teste de integração: DELETE /tags/{id}"""
        response = client.delete(f"/api/v1/tags/{test_tag.id}", headers=auth_headers)

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_tag_not_found(self, client: TestClient, auth_headers: dict):
        """Teste: erro ao acessar tag inexistente"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/tags/{fake_uuid}", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unauthorized_tag_access(self, client: TestClient):
        """Teste: acesso não autorizado às tags"""
        responses = [
            client.get("/api/v1/tags/"),
            client.post("/api/v1/tags/", json={"name": "Test"}),
        ]

        for response in responses:
            assert response.status_code == 401


@pytest.mark.parametrize(
    "name,color,expected_status",
    [
        ("Valid Tag", "#FF0000", 200),
        ("Another Tag", "#00FF00", 200),
        ("", "#FF0000", 422),  # Nome vazio
        (
            "Valid Tag",
            "invalid-color",
            200,
        ),  # Cor inválida é aceita (validação opcional)
    ],
)
def test_create_tag_validation(
    client: TestClient, auth_headers: dict, name: str, color: str, expected_status: int
):
    """US#7 - Testes parametrizados: validação na criação de tags"""
    tag_data = {"name": name, "color": color}

    response = client.post("/api/v1/tags/", json=tag_data, headers=auth_headers)
    assert response.status_code == expected_status


class TestTagFlow:
    """Testes de fluxo completo de tags"""

    def test_complete_tag_management_flow(self, client: TestClient, auth_headers: dict):
        """US#7 - Fluxo: Criar → Listar → Atualizar → Deletar tag"""
        # 1. Criar tag
        create_response = client.post(
            "/api/v1/tags/",
            json={"name": "Flow Tag", "color": "#FF00FF"},
            headers=auth_headers,
        )

        assert create_response.status_code == 200
        tag_id = create_response.json()["id"]

        # 2. Listar e verificar se aparece
        list_response = client.get("/api/v1/tags/", headers=auth_headers)
        assert list_response.status_code == 200
        tag_names = [tag["name"] for tag in list_response.json()]
        assert "Flow Tag" in tag_names

        # 3. Atualizar
        update_response = client.put(
            f"/api/v1/tags/{tag_id}",
            json={"name": "Updated Flow Tag", "color": "#00FFFF"},
            headers=auth_headers,
        )

        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Flow Tag"

        # 4. Deletar
        delete_response = client.delete(f"/api/v1/tags/{tag_id}", headers=auth_headers)
        assert delete_response.status_code == 200
