# Crie o arquivo: backend/src/users/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from . import schema
from .repository import UserRepository

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schema.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schema.UserCreate, 
    db: Session = Depends(get_db), 
    repo: UserRepository = Depends()
):
    db_user = repo.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    return repo.create_user(db=db, user=user)