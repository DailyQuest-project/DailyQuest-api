"""Test configuration and fixtures for DailyQuest API tests.

This module provides pytest fixtures for database sessions, test clients,
authentication, and test data creation for comprehensive API testing.
"""

import os
from datetime import datetime, timedelta
from typing import Dict

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
from src.security import hash_password, create_access_token

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
    # Definir variável de ambiente para usar validação local
    os.environ["TESTING"] = "true"

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

    # Limpar a variável de ambiente após o teste
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def test_user_credentials():
    """Fixture que define as credenciais do usuário de teste."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }


@pytest.fixture
def test_user(db_session, test_user_credentials):
    """Fixture que obtém o usuário de teste criado pelo seed."""
    # Buscar o usuário de teste criado pelo seed
    user = (
        db_session.query(User)
        .filter(User.username == test_user_credentials["username"])
        .first()
    )

    # Se não existir (caso raro), criar um novo
    if not user:
        user = User(
            username=test_user_credentials["username"],
            email=test_user_credentials["email"],
            password_hash=hash_password(test_user_credentials["password"]),
            xp=0,
            level=1,
            coins=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    return user


@pytest.fixture
def real_access_token(test_user):
    """Fixture que cria um token JWT válido para o usuário de teste."""
    # Criar token JWT válido usando a mesma lógica da aplicação
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": test_user.username}, expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture
def auth_headers(real_access_token):
    """Fixture que cria headers de autenticação com token real."""
    return {"Authorization": f"Bearer {real_access_token}"}


@pytest.fixture
def auth_client(client, auth_headers):
    """Fixture que retorna um cliente já autenticado com token real."""
    client.headers.update(auth_headers)
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
