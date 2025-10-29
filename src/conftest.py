"""Test configuration and fixtures for DailyQuest API tests.

This module provides pytest fixtures for database sessions, test clients,
authentication, and test data creation for comprehensive API testing.
"""
import os

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
from src.task.model import Habit, ToDo
from src.utils import hash_password

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
def client(session):
    """Fixture que cria um cliente de teste do FastAPI."""

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(session):
    """Fixture que cria um usuário de teste."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        xp=0,
        level=1,
        coins=0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_client, _):
    """Fixture que cria headers de autenticação."""
    response = test_client.post(
        "/api/v1/auth/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_client(test_client, _):
    """
    Fixture que retorna um cliente já autenticado.
    Útil para testes que precisam de autenticação sem configurar manualmente.
    """
    response = test_client.post(
        "/api/v1/auth/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json()["access_token"]
    test_client.headers.update({"Authorization": f"Bearer {token}"})
    return test_client


@pytest.fixture
def test_achievement(session):
    """Fixture que cria uma conquista de teste."""
    achievement = Achievement(
        name="Test Achievement",
        description="Test achievement description",
        icon="🏆",
        category="Test",
        requirement_key=AchievementKey.FIRST_HABIT,
    )
    session.add(achievement)
    session.commit()
    session.refresh(achievement)
    return achievement


@pytest.fixture
def seeded_achievements(session):
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
        session.add(achievement)
        achievements.append(achievement)

    session.commit()
    return achievements


@pytest.fixture
def test_tag(session, user):
    """Fixture que cria uma tag de teste."""
    tag = Tag(name="Test Tag", color="#FF0000", user_id=user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@pytest.fixture
def test_habit(session, user):
    """Fixture que cria um hábito de teste."""
    habit = Habit(
        title="Test Habit",
        description="Test habit description",
        user_id=user.id,
        difficulty="EASY",
        frequency_type="DAILY",
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@pytest.fixture
def test_todo(session, user):
    """Fixture que cria um todo de teste."""
    todo = ToDo(
        title="Test Todo",
        description="Test todo description",
        user_id=user.id,
        difficulty="MEDIUM",
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
