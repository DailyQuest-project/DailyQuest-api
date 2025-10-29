"""User repository for database operations in DailyQuest API.

This module provides data access methods for user management
including user creation, authentication, and user lookup operations.
"""

from uuid import UUID
from sqlalchemy.orm import Session
from . import model, schema
from ..utils import hash_password


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
        db.commit()
        db.refresh(db_user)
        return db_user
