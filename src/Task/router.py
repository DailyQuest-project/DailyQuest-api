from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
from ..deps import get_db, get_current_user
from ..users.model import User
from . import schema
from .repository import TaskRepository
from ..tags.repository import TagRepository as TagRepo

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Dependency para o repository
def get_task_repository() -> TaskRepository:
    return TaskRepository()


# Dependency para o tag repository
def get_tag_repository() -> TagRepo:
    return TagRepo()


# US#3 - Criar hábito
@router.post("/habits/", response_model=schema.HabitResponse)
def create_habit(
    habit: schema.HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.HabitResponse:
    return repo.create_habit(db=db, habit=habit, user_id=current_user.id)


# US#8 - Criar ToDo
@router.post("/todos/", response_model=schema.ToDoResponse)
def create_todo(
    todo: schema.ToDoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.ToDoResponse:
    return repo.create_todo(db=db, todo=todo, user_id=current_user.id)


# US#6 - Listar todas as tarefas (hábitos e todos)
@router.get("/", response_model=List[schema.TaskResponse])
def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> List[schema.TaskResponse]:
    return repo.get_tasks_by_user(db=db, user_id=current_user.id)


# US#10 - Atualizar hábito
@router.put("/habits/{habit_id}", response_model=schema.HabitResponse)
def update_habit(
    habit_id: UUID,
    habit_update: schema.HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.HabitResponse:
    updated_habit = repo.update_habit(
        db=db, habit_id=habit_id, user_id=current_user.id, habit_update=habit_update
    )

    if not updated_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )

    return updated_habit


# US#10 - Deletar hábito
@router.delete("/habits/{habit_id}")
def delete_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> Dict[str, str]:
    deleted = repo.delete_habit(db=db, habit_id=habit_id, user_id=current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )

    return {"message": "Habit deleted successfully"}


# --- ROTA 1: Associar Tag a uma Tarefa ---
@router.post("/{task_id}/tags/{tag_id}", response_model=schema.TaskResponse)
def add_tag_to_task_endpoint(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    task_repo: TaskRepository = Depends(get_task_repository),
    tag_repo: TagRepo = Depends(get_tag_repository),
) -> schema.TaskResponse:
    """Associa uma tag existente a uma tarefa."""
    # 1. Busca a tarefa
    task = task_repo.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Busca a tag
    tag = tag_repo.get_tag_by_id(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 3. Associa
    return task_repo.add_tag_to_task(db, task, tag)


# --- ROTA 2: Desassociar Tag de uma Tarefa ---
@router.delete("/{task_id}/tags/{tag_id}", response_model=schema.TaskResponse)
def remove_tag_from_task_endpoint(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    task_repo: TaskRepository = Depends(get_task_repository),
    tag_repo: TagRepo = Depends(get_tag_repository),
) -> schema.TaskResponse:
    """Desassocia uma tag de uma tarefa."""
    task = task_repo.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = tag_repo.get_tag_by_id(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return task_repo.remove_tag_from_task(db, task, tag)


# --- ROTA 3: Filtrar Tarefas por Tag (US#12) ---
@router.get("/by-tag/{tag_id}", response_model=List[schema.TaskResponse])
def get_tasks_by_tag_endpoint(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    task_repo: TaskRepository = Depends(get_task_repository),
    tag_repo: TagRepo = Depends(get_tag_repository),
) -> List[schema.TaskResponse]:
    """
    Retorna todas as tarefas do usuário filtradas por uma tag (US#12).
    """
    # Valida se a tag existe e pertence ao usuário
    tag = tag_repo.get_tag_by_id(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return task_repo.get_tasks_by_tag(db, current_user.id, tag_id)
