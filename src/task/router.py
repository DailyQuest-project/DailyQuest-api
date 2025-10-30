"""Task router for CRUD operations in DailyQuest API.

This module provides REST API endpoints for task management
including habits and todos creation, updates, deletion, and tag associations.
"""

from typing import List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..users.model import User
from . import schema
from .repository import TaskRepository
from ..tags.repository import TagRepository as TagRepo

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_repository() -> TaskRepository:
    """Dependency to provide TaskRepository instance."""
    return TaskRepository()


def get_tag_repository() -> TagRepo:
    """Dependency to provide TagRepository instance."""
    return TagRepo()


def get_repositories() -> tuple[TaskRepository, TagRepo]:
    """Dependency to provide both TaskRepository and TagRepository instances."""
    return TaskRepository(), TagRepo()


@router.post(
    "/habits/", response_model=schema.HabitResponse, status_code=status.HTTP_201_CREATED
)
def create_habit(
    habit: schema.HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.HabitResponse:
    """Create a new habit for the authenticated user."""
    return repo.create_habit(db=db, habit=habit, user_id=current_user.id)


@router.post(
    "/todos/", response_model=schema.ToDoResponse, status_code=status.HTTP_201_CREATED
)
def create_todo(
    todo: schema.ToDoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.ToDoResponse:
    """Create a new todo for the authenticated user."""
    return repo.create_todo(db=db, todo=todo, user_id=current_user.id)


@router.get("/", response_model=List[schema.TaskResponse])
def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> List[schema.TaskResponse]:
    """Get all tasks (habits and todos) for the authenticated user."""
    return repo.get_tasks_by_user(db=db, user_id=current_user.id)


@router.put("/habits/{habit_id}", response_model=schema.HabitResponse)
def update_habit(
    habit_id: UUID,
    habit_update: schema.HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.HabitResponse:
    """Update an existing habit for the authenticated user."""
    updated_habit = repo.update_habit(
        db=db, habit_id=habit_id, user_id=current_user.id, habit_update=habit_update
    )

    if not updated_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )

    return updated_habit


@router.put("/todos/{todo_id}", response_model=schema.ToDoResponse)
def update_todo(
    todo_id: UUID,
    todo_update: schema.ToDoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> schema.ToDoResponse:
    """Update an existing ToDo for the authenticated user."""
    updated_todo = repo.update_todo(
        db=db, todo_id=todo_id, user_id=current_user.id, todo_update=todo_update
    )

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not found"
        )

    return updated_todo


@router.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> Dict[str, str]:
    """Delete a ToDo for the authenticated user."""
    deleted = repo.delete_todo(db=db, todo_id=todo_id, user_id=current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not found"
        )

    return {"message": "ToDo deleted successfully"}


@router.delete("/habits/{habit_id}")
def delete_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TaskRepository = Depends(get_task_repository),
) -> Dict[str, str]:
    """Delete a habit for the authenticated user."""
    deleted = repo.delete_habit(db=db, habit_id=habit_id, user_id=current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )

    return {"message": "Habit deleted successfully"}


@router.post("/{task_id}/tags/{tag_id}", response_model=schema.TaskResponse)
def add_tag_to_task_endpoint(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repos: tuple[TaskRepository, TagRepo] = Depends(get_repositories),
) -> schema.TaskResponse:
    """Associate an existing tag with a task."""
    task_repo, tag_repo = repos
    task = task_repo.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = tag_repo.get_tag_by_id(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return task_repo.add_tag_to_task(db, task, tag)


@router.delete("/{task_id}/tags/{tag_id}", response_model=schema.TaskResponse)
def remove_tag_from_task_endpoint(
    task_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repos: tuple[TaskRepository, TagRepo] = Depends(get_repositories),
) -> schema.TaskResponse:
    """Remove a tag association from a task."""
    task_repo, tag_repo = repos
    task = task_repo.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = tag_repo.get_tag_by_id(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return task_repo.remove_tag_from_task(db, task, tag)


@router.get("/by-tag/{tag_id}", response_model=List[schema.TaskResponse])
def get_tasks_by_tag_endpoint(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repos: tuple[TaskRepository, TagRepo] = Depends(get_repositories),
) -> List[schema.TaskResponse]:
    """Get all user tasks filtered by a specific tag (US#12)."""
    task_repo, tag_repo = repos
    tag = tag_repo.get_tag_by_id(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return task_repo.get_tasks_by_tag(db, current_user.id, tag_id)
