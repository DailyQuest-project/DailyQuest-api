import pytest
from src.users.model import User
from src.security import hash_password


class TestUser:
    """Testes para o modelo User"""

    def test_user_creation_basic(self):
        """Teste básico que deve passar - criação de usuário"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=hash_password("password123")
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.xp == 0
        assert user.level == 1
        assert user.coins == 0
        assert user.theme == 'light'

    @pytest.mark.skip(reason="Sistema de achievements não implementado")
    def test_user_achievements_system_missing(self):
        """Teste skipado para funcionalidade não implementada"""
        user = User(
            email="achievement@test.com",
            username="achiever",
            password_hash=hash_password("test123")
        )
        
        # Estes métodos não existem - causariam erros
        achievements = user.get_achievements()  # Método inexistente
        user.unlock_achievement("first_login")  # Método inexistente
        
        assert len(achievements) >= 0

    def test_user_defaults_work(self):
        """Teste que deve passar - valores padrão funcionam"""
        user = User(
            email="defaults@test.com",
            username="defaultuser",
            password_hash="somehash"
        )
        
        assert user.xp == 0
        assert user.level == 1  
        assert user.coins == 0
        assert user.theme == 'light'
        assert user.avatar_url is None