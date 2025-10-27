# Em: src/dashboard/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..deps import get_db, get_current_user
from ..users.model import User
from . import schema
from .repository import DashboardRepository

router = APIRouter(prefix="/dashboard", tags=["Dashboard & History"])

def get_dashboard_repository():
    return DashboardRepository()

@router.get("/history", response_model=List[schema.HistoryItem])
def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: DashboardRepository = Depends(get_dashboard_repository),
):
    """
    Retorna o histórico de todas as tarefas completadas pelo usuário (US#9).
    """
    return repo.get_completion_history(db, user_id=current_user.id)

@router.get("/", response_model=schema.DashboardStats)
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: DashboardRepository = Depends(get_dashboard_repository),
):
    """
    Retorna as estatísticas agregadas para o dashboard do usuário (US#19).
    """
    return repo.get_dashboard_stats(db, user=current_user)
