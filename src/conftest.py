# Em: src/conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database import get_db, Base
from src.users.model import User
from src.achievements.model import Achievement, AchievementKey
from src.tags.model import Tag
from src.Task.model import Habit, ToDo
from src.utils import hash_password

# --- Configuração do Banco de Dados de Teste ---
# LÊ A URL DO AMBIENTE (definida no docker-compose.yml ou usa SQLite como fallback)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# Configurações específicas por tipo de banco
engine_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite precisa de configurações especiais para threads
    engine_args = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
elif SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    # PostgreSQL não precisa dessas configurações
    # psycopg2 já lida com threads corretamente
    engine_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture que cria uma sessão de banco de dados para cada teste."""
    # Garante que está limpo antes de criar
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Limpa depois do teste
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
def auth_headers(client, test_user):
    """Fixture que cria headers de autenticação."""
    response = client.post(
        "/api/v1/auth/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_client(client, test_user):
    """
    Fixture que retorna um cliente já autenticado.
    Útil para testes que precisam de autenticação sem configurar manualmente.
    """
    response = client.post(
        "/api/v1/auth/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
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
        difficulty="EASY",
        frequency_type="DAILY",
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
        difficulty="MEDIUM",
    )
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo
