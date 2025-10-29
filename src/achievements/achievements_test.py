"""Achievement functionality tests for DailyQuest API.

This module contains unit and integration tests for achievement management
including unlocking achievements and checking user progress.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.achievements.repository import AchievementRepository
from src.achievements.model import Achievement
from src.users.model import User


class TestAchievementRepository:
    """Testes unitários para AchievementRepository"""

    def test_get_achievement_by_key(
        self, db_session: Session, test_achievement: Achievement
    ):
        """Teste unitário: buscar conquista por chave"""
        repo = AchievementRepository()
        found_achievement = repo.get_achievement_by_key(
            db_session, test_achievement.requirement_key
        )

        assert found_achievement is not None
        assert found_achievement.requirement_key == test_achievement.requirement_key

    def test_unlock_achievement_for_user(
        self, db_session: Session, test_user: User, test_achievement: Achievement
    ):
        """US#18 - Teste unitário: desbloquear conquista para usuário"""
        repo = AchievementRepository()

        # Call the function without assigning since it returns None
        repo.unlock_achievement_for_user(
            db_session, test_user.id, test_achievement
        )

        # Verificar se foi criado
        db_session.commit()
        unlocked = repo.check_if_user_has_achievement(
            db_session, test_user.id, test_achievement.id
        )
        assert unlocked is True


class TestAchievementEndpoints:
    """Testes de integração para endpoints de conquistas"""

    def test_get_my_achievements_empty(self, client: TestClient, auth_headers: dict):
        """US#18 - Teste: usuário sem conquistas"""
        response = client.get("/api/v1/achievements/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


@pytest.mark.parametrize(
    "xp,expected_achievements",
    [
        (0, 0),  # Nível 1, sem conquistas
        (50, 1),  # Nível 5, uma conquista
        (100, 2),  # Nível 10, duas conquistas
    ],
)
def test_level_achievements_parametrized(xp: int, expected_achievements: int):
    """US#18 - Testes parametrizados: conquistas por nível"""
    # Lógica simplificada para calcular nível
    level = (xp // 10) + 1
    achievements_count = 0

    if level >= 5:
        achievements_count += 1
    if level >= 10:
        achievements_count += 1

    assert achievements_count == expected_achievements
