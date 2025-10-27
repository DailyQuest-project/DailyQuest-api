from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..deps import get_db, get_current_user
from ..users.model import User
from . import schema
from .repository import TagRepository

router = APIRouter(prefix="/tags", tags=["Tags"])

def get_tag_repository():
    return TagRepository()

@router.post("/", response_model=schema.TagResponse)
def create_tag(
    tag: schema.TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TagRepository = Depends(get_tag_repository),
):
    """
    Cria uma nova tag (US#7) para o usuário logado.
    """
    return repo.create_tag(db=db, tag=tag, user_id=current_user.id)

@router.get("/", response_model=List[schema.TagResponse])
def get_user_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TagRepository = Depends(get_tag_repository),
):
    """
    Lista todas as tags do usuário logado.
    """
    return repo.get_tags_by_user(db=db, user_id=current_user.id)


@router.get("/{tag_id}", response_model=schema.TagResponse)
def get_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TagRepository = Depends(get_tag_repository),
):
    """
    Busca uma tag específica do usuário logado.
    """
    tag = repo.get_tag_by_id(db=db, tag_id=tag_id, user_id=current_user.id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    return tag

@router.put("/{tag_id}", response_model=schema.TagResponse)
def update_tag(
    tag_id: UUID,
    tag_update: schema.TagUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TagRepository = Depends(get_tag_repository),
):
    """
    Atualiza uma tag do usuário logado.
    """
    updated_tag = repo.update_tag(
        db=db, tag_id=tag_id, user_id=current_user.id, tag_update=tag_update
    )

    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    return updated_tag

@router.delete("/{tag_id}")
def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo: TagRepository = Depends(get_tag_repository),
):
    """
    Deleta uma tag do usuário logado.
    """
    deleted = repo.delete_tag(db=db, tag_id=tag_id, user_id=current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    return {"message": "Tag deleted successfully"}
