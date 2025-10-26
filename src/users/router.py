# Em: src/users/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schema
from .repository import UserRepository
from ..users.model import User as UserModel
from ..deps import get_db, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schema.User)
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

@router.get("/me", response_model=schema.User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user

