"""User router for CRUD operations in DailyQuest API.

This module provides REST API endpoints for user management
including user registration and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schema
from .repository import UserRepository
from ..users.model import User as UserModel
from ..deps import get_db, get_current_user
from ..achievements.repository import AchievementRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schema.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schema.UserCreate,
    db: Session = Depends(get_db),
    repo: UserRepository = Depends(),
) -> schema.User:
    """Register a new user account."""
    # Check if email already exists
    db_user = repo.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username already exists
    db_user_username = repo.get_user_by_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    return repo.create_user(db=db, user=user)


@router.get("/me", response_model=schema.User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserModel:
    """Get the current authenticated user's profile and unlock FIRST_LOGIN achievement."""

    # Desbloquear conquista de primeiro login
    achievement_repo = AchievementRepository()
    try:
        achievement_repo.check_first_login_achievement(db, current_user.id)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Não bloquear o login se houver erro ao desbloquear conquista
        print(f"⚠️ Erro ao verificar conquista FIRST_LOGIN: {e}")

    return current_user
