"""Database seeding module for DailyQuest API.

This module provides functionality to seed the database with initial data,
particularly achievements data that are required for the application to function.
"""

import sys
import os
from typing import Dict, Any, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL
from src.achievements.model import Achievement, AchievementKey

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


def seed_database() -> None:
    """Seed the database with initial achievements data.

    Creates default achievements in the database if they don't already exist.
    This function is idempotent - it can be safely run multiple times.
    """
    print(" Iniciando o seeding do banco de dados...")
    db = SESSIONLOCAL()

    try:
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

        db.commit()
        print(" Seeding concluído com sucesso!")
        print(f" Total de conquistas no banco: {db.query(Achievement).count()}")
    except Exception as e:
        print(f" Erro durante o seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
