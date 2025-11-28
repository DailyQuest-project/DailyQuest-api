"""User repository for database operations in DailyQuest API.

This module provides data access methods for user management
including user creation, authentication, and user lookup operations.
"""

from uuid import UUID
from sqlalchemy.orm import Session
from . import model, schema
from ..utils import hash_password
from ..tags.model import Tag
from ..task.model import Habit, Difficulty, HabitFrequencyType


class UserRepository:
    """Repository for user-related database operations."""

    def get_user_by_id(self, db: Session, user_id: UUID):
        """Get user by ID."""
        return db.query(model.User).filter(model.User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str):
        """Get user by email address."""
        return db.query(model.User).filter(model.User.email == email).first()

    def get_user_by_username(self, db: Session, username: str):
        """Get user by username."""
        return db.query(model.User).filter(model.User.username == username).first()

    def create_user(self, db: Session, user: schema.UserCreate):
        """Create a new user with hashed password."""
        hashed_pass = hash_password(user.password)

        db_user = model.User(
            username=user.username, email=user.email, password_hash=hashed_pass
        )
        db.add(db_user)
        db.flush()  # Flush para gerar o ID do usuário antes de criar tags e hábitos

        # Criar tags iniciais para o novo usuário
        initial_tags = self._create_initial_tags(db, db_user.id)

        # Criar hábito padrão
        health_tag = next((tag for tag in initial_tags if tag.name == "Saúde"), None)
        self._create_default_habit(db, db_user.id, health_tag.id if health_tag else None)

        db.commit()
        db.refresh(db_user)
        return db_user

    def _create_initial_tags(self, db: Session, user_id):
        """Create initial tags for a new user."""
        initial_tags_data = [
            {"name": "Saúde", "color": "#4CAF50"},  # Verde
            {"name": "Estudo", "color": "#2196F3"},  # Azul
            {"name": "Trabalho", "color": "#FF9800"},  # Laranja
            {"name": "Exercício", "color": "#F44336"},  # Vermelho
            {"name": "Bem-estar", "color": "#9C27B0"},  # Roxo
            {"name": "Produtividade", "color": "#00BCD4"},  # Ciano
        ]

        created_tags = []
        for tag_data in initial_tags_data:
            tag = Tag(
                user_id=user_id,
                name=tag_data["name"],
                color=tag_data["color"]
            )
            db.add(tag)
            created_tags.append(tag)

        db.flush()
        return created_tags

    def _create_default_habit(self, db: Session, user_id, health_tag_id=None):
        """Create a default 'Drink Water' habit for new users."""
        # pylint: disable=import-outside-toplevel
        from sqlalchemy import text as sql_text

        default_habit = Habit(
            title="💧 Beber 2L de Água",
            description=(
                "Manter-se hidratado é essencial para a saúde. "
                "Beba pelo menos 2 litros de água por dia!"
            ),
            user_id=user_id,
            difficulty=Difficulty.EASY,
            frequency_type=HabitFrequencyType.DAILY,
            is_active=True,
            current_streak=0
        )

        db.add(default_habit)
        db.flush()

        # Associar tag de Saúde se disponível
        if health_tag_id:
            db.execute(
                sql_text(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (:task_id, :tag_id)"
                ),
                {"task_id": default_habit.id, "tag_id": health_tag_id}
            )

        return default_habit
