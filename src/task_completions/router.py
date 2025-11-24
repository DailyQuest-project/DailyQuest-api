"""Task completion router for REST API endpoints in DailyQuest API.

This module provides REST API endpoints for task completion management
using the TaskService layer for business logic orchestration.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..users.model import User
from ..task.service import TaskService, TaskAlreadyCompletedError, TaskNotFoundError
from ..task.repository import TaskRepository
from ..users.repository import UserRepository
from ..achievements.repository import AchievementRepository
from . import schema
from .repository import TaskCompletionRepository

router = APIRouter(prefix="/tasks", tags=["Task Completions"])


def get_task_service() -> TaskService:
    """Dependency to provide TaskService instance with all required repositories."""
    return TaskService(
        task_repo=TaskRepository(),
        completion_repo=TaskCompletionRepository(),
        user_repo=UserRepository(),
        achievement_repo=AchievementRepository(),
    )


# US#4 - Endpoint de Check-in (refatorado para usar TaskService)
@router.post("/{task_id}/complete", response_model=schema.CheckInResponse)
def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: TaskService = Depends(get_task_service),
) -> schema.CheckInResponse:
    """
    Endpoint de check-in para completar tarefas (US#4)

    Este endpoint agora delega toda a lógica de negócio complexa para o TaskService,
    mantendo apenas a responsabilidade de:
    - Autenticação e autorização
    - Conversão de exceções de negócio para HTTP responses
    - Serialização da resposta
    """
    try:
        # Inject database session into the service
        service.set_db_session(db)

        # Delegate all business logic to the service layer
        completion_result = service.complete_task(
            task_id=task_id, user_id=current_user.id
        )

        # Convert service response to API response schema
        return schema.CheckInResponse(
            message=completion_result["message"],
            task_completion=completion_result["task_completion"],
            user=completion_result["user"],
            streak_updated=completion_result["streak_updated"],
            new_streak=completion_result["new_streak"],
        )

    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except TaskAlreadyCompletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while completing the task",
        ) from e


@router.delete("/{task_id}/complete", status_code=status.HTTP_200_OK)
def uncomplete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Endpoint para remover a conclusão de hoje de uma tarefa.
    Permite que o usuário "desmarque" uma tarefa que completou hoje.
    """
    from datetime import datetime, timedelta
    from ..task.model import Task, Habit, ToDo
    from .model import TaskCompletion
    
    # Verificar se a tarefa existe e pertence ao usuário
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Buscar a conclusão de hoje
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    completion = (
        db.query(TaskCompletion)
        .filter(
            TaskCompletion.task_id == task_id,
            TaskCompletion.user_id == current_user.id,
            TaskCompletion.completed_date >= today_start,
            TaskCompletion.completed_date < today_end,
        )
        .first()
    )
    
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completion found for today"
        )
    
    # Reverter XP do usuário
    xp_to_remove = completion.xp_earned
    current_user.xp = max(0, current_user.xp - xp_to_remove)
    
    # Se for habit, reverter streak
    if isinstance(task, Habit):
        task.current_streak = max(0, task.current_streak - 1)
        task.last_completed = None
    
    # Se for todo, desmarcar como completado
    if isinstance(task, ToDo):
        task.completed = False
    
    # Deletar o registro de conclusão
    db.delete(completion)
    db.commit()
    
    return {
        "message": "Task completion removed successfully",
        "xp_removed": xp_to_remove
    }
