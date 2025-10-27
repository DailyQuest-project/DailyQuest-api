# Em: src/achievements/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..deps import get_db, get_current_user
from ..users.model import User
from . import schema
from .repository import AchievementRepository

router = APIRouter(prefix="/achievements", tags=["Achievements"])


def get_achievement_repository():
    return AchievementRepository()


# US#18 - Endpoint de Conquistas
@router.get("/me", response_model=List[schema.UserAchievementResponse])
def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: AchievementRepository = Depends(get_achievement_repository),
):
    """
    Retorna a lista de todas as conquistas desbloqueadas pelo usuário (US#18).
    """
    return repo.list_user_achievements(db, user_id=current_user.id)
