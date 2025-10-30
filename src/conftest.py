"""Test configuration and fixtures for DailyQuest API tests.

This module provides pytest fixtures for database sessions, test clients,
authentication, and test data creation for comprehensive API testing.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base
from src.users.model import User
from src.achievements.model import Achievement, AchievementKey
from src.tags.model import Tag
from src.task.model import Habit, ToDo, Difficulty, HabitFrequencyType
from src.security import hash_password

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

engine_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_args = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
elif SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    engine_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)
TESTING_SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture que cria uma sessão de banco de dados para cada teste."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TESTING_SESSIONLOCAL()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture que cria um cliente de teste do FastAPI."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Fixture que cria um usuário de teste."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        xp=0,
        level=1,
        coins=0,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Fixture que cria headers de autenticação mockados."""
    # Como não temos mais o endpoint de auth local, usamos um token mock
    return {"Authorization": "Bearer mock_token_for_testing"}


@pytest.fixture
def auth_client(client, test_user):
    """
    Fixture que retorna um cliente já autenticado com mock do serviço de auth.
    """
    # Mock da resposta do serviço de autenticação
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"username": test_user.username}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        client.headers.update({"Authorization": "Bearer mock_token_for_testing"})
        return client


@pytest.fixture
def test_achievement(db_session):
    """Fixture que cria uma conquista de teste."""
    achievement = Achievement(
        name="Test Achievement",
        description="Test achievement description",
        icon="🏆",
        category="Test",
        requirement_key=AchievementKey.FIRST_HABIT,
    )
    db_session.add(achievement)
    db_session.commit()
    db_session.refresh(achievement)
    return achievement


@pytest.fixture
def seeded_achievements(db_session):
    """Fixture que cria todas as conquistas padrão do sistema."""
    achievements_data = [
        {"name": "Nível 5", "requirement_key": AchievementKey.LEVEL_5},
        {"name": "Nível 10", "requirement_key": AchievementKey.LEVEL_10},
        {"name": "Criador de Hábitos", "requirement_key": AchievementKey.FIRST_HABIT},
        {"name": "Primeira Tarefa", "requirement_key": AchievementKey.FIRST_TODO},
        {"name": "Em Chamas!", "requirement_key": AchievementKey.STREAK_3},
        {"name": "Implacável", "requirement_key": AchievementKey.STREAK_7},
    ]

    achievements = []
    for data in achievements_data:
        achievement = Achievement(
            name=data["name"],
            description=f"Achievement: {data['name']}",
            icon="🏆",
            category="Test",
            requirement_key=data["requirement_key"],
        )
        db_session.add(achievement)
        achievements.append(achievement)

    db_session.commit()
    return achievements


@pytest.fixture
def test_tag(db_session, test_user):
    """Fixture que cria uma tag de teste."""
    tag = Tag(name="Test Tag", color="#FF0000", user_id=test_user.id)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture
def test_habit(db_session, test_user):
    """Fixture que cria um hábito de teste."""
    habit = Habit(
        title="Test Habit",
        description="Test habit description",
        user_id=test_user.id,
        difficulty=Difficulty.EASY,
        frequency_type=HabitFrequencyType.DAILY,
    )
    db_session.add(habit)
    db_session.commit()
    db_session.refresh(habit)
    return habit


@pytest.fixture
def test_todo(db_session, test_user):
    """Fixture que cria um todo de teste."""
    todo = ToDo(
        title="Test Todo",
        description="Test todo description",
        user_id=test_user.id,
        difficulty=Difficulty.MEDIUM,
    )
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo
