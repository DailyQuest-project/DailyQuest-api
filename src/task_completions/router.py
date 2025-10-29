"""Task completion router for REST API endpoints in DailyQuest API.

This module provides REST API endpoints for task completion management
including task check-in and completion tracking with XP and streak updates.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..users.model import User
from . import schema
from .repository import TaskCompletionRepository

router = APIRouter(prefix="/tasks", tags=["Task Completions"])


def get_task_completion_repository() -> TaskCompletionRepository:
    """Dependency to provide TaskCompletionRepository instance."""
    return TaskCompletionRepository()


# US#4 - Endpoint de Check-in (o mais complexo)
@router.post("/{task_id}/complete", response_model=schema.CheckInResponse)
def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskCompletionRepository = Depends(get_task_completion_repository),
) -> schema.CheckInResponse:
    """
    Endpoint de check-in para completar tarefas (US#4)

    Este endpoint:
    - Verifica se a tarefa pertence ao usuário atual
    - Calcula o XP ganho baseado na dificuldade (US#5, US#11)
    - Cria um novo TaskCompletion no banco com o XP
    - Atualiza o User com o novo XP
    - Se for Habit, atualiza o current_streak (US#14)
    - Se for ToDo, marca como completado
    - Retorna o usuário atualizado e status da tarefa
    """
    try:
        # Unpack the tuple returned by complete_task
        task_completion, updated_user, streak_updated, new_streak = repo.complete_task(
            db=db, task_id=task_id, user_id=UUID(str(current_user.id))
        )

        return schema.CheckInResponse(
            message=f"Task completed! XP earned: {task_completion.xp_earned}.",
            task_completion=task_completion,
            user=updated_user,
            streak_updated=streak_updated,
            new_streak=new_streak,
        )

    except ValueError as e:
        if str(e) == "Task not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to current user",
            ) from e
        if str(e) == "Task already completed today":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task has already been completed today",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
