"""Database seeding module for DailyQuest API.

This module provides functionality to seed the database with initial data,
particularly achievements data and test users required for the application to function.
"""

import sys
import os
from typing import Dict, Any, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL
from src.achievements.model import Achievement, AchievementKey
from src.users.model import User
from src.security import hash_password

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

engine = create_engine(DATABASE_URL)
SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ACHIEVEMENTS_TO_SEED: List[Dict[str, Any]] = [
    {
        "name": "Nível 5",
        "description": "Alcance o Nível 5.",
        "icon": "🏆",
        "category": "Progressão",
        "requirement_key": AchievementKey.LEVEL_5,
    },
    {
        "name": "Nível 10",
        "description": "Alcance o Nível 10.",
        "icon": "⭐",
        "category": "Progressão",
        "requirement_key": AchievementKey.LEVEL_10,
    },
    {
        "name": "Criador de Hábitos",
        "description": "Complete um hábito pela primeira vez.",
        "icon": "🎯",
        "category": "Primeiros Passos",
        "requirement_key": AchievementKey.FIRST_HABIT,
    },
    {
        "name": "Primeira Tarefa",
        "description": "Complete um ToDo pela primeira vez.",
        "icon": "✅",
        "category": "Primeiros Passos",
        "requirement_key": AchievementKey.FIRST_TODO,
    },
    {
        "name": "Em Chamas!",
        "description": "Alcance uma sequência de 3 dias em qualquer hábito.",
        "icon": "🔥",
        "category": "Streaks",
        "requirement_key": AchievementKey.STREAK_3,
    },
    {
        "name": "Implacável",
        "description": "Alcance uma sequência de 7 dias em qualquer hábito.",
        "icon": "🚀",
        "category": "Streaks",
        "requirement_key": AchievementKey.STREAK_7,
    },
]


def seed_test_user(db) -> None:
    """Create a test user for development and testing purposes.

    Creates a test user with known credentials that can be used in tests.
    This function is idempotent - it can be safely run multiple times.
    """
    # Verificar se o usuário de teste já existe
    existing_user = db.query(User).filter(User.username == "testuser").first()

    if not existing_user:
        print("  Criando usuário de teste...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("testpass123"),
            xp=0,
            level=1,
            coins=0,
            theme="light",
        )
        db.add(test_user)
        db.commit()
        print("  ✅ Usuário de teste criado: testuser")
    else:
        print("  ℹ️  Usuário de teste já existe: testuser")


def seed_database() -> None:
    """Seed the database with initial data.

    Creates default achievements and test users in the database if they don't already exist.
    This function is idempotent - it can be safely run multiple times.
    """
    print(" Iniciando o seeding do banco de dados...")
    db = SESSIONLOCAL()

    try:
        # Seed achievements
        for ach_data in ACHIEVEMENTS_TO_SEED:
            exists = (
                db.query(Achievement)
                .filter(Achievement.requirement_key == ach_data["requirement_key"])
                .count()
                > 0
            )

            if not exists:
                new_ach = Achievement(**ach_data)
                db.add(new_ach)
                print(f"  Criando conquista: {ach_data['name']} {ach_data['icon']}")
            else:
                print(f"  Conquista já existe: {ach_data['name']}")

        # Seed test user
        seed_test_user(db)

        db.commit()
        print(" Seeding concluído com sucesso!")
        print(f" Total de conquistas no banco: {db.query(Achievement).count()}")
        print(f" Total de usuários no banco: {db.query(User).count()}")
    except Exception as e:
        print(f" Erro durante o seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
