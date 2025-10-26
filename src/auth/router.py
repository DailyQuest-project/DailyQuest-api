# Em: src/auth/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..deps import get_db
from ..users.repository import UserRepository
from ..security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    repo: UserRepository = Depends()
):
    # 1. Busca o usuário pelo username (que vem no form_data.username)
    user = repo.get_user_by_username(db, username=form_data.username)

    # 2. Verifica se o usuário existe e se a senha está correta
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Cria o token JWT. O "sub" (subject) é o username.
    access_token_data = {"sub": user.username}
    access_token = create_access_token(data=access_token_data)

    # 4. Retorna o token
    return {"access_token": access_token, "token_type": "bearer"}