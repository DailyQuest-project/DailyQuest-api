# Crie este arquivo: src/deps.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from .database import SessionLocal
from .security import oauth2_scheme, SECRET_KEY, ALGORITHM
from .users.repository import UserRepository
from .users.model import User

# --- Dependência 1: Obter a Sessão do Banco ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dependência 2: Obter o Usuário Logado (Movido de security.py) ---
def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    repo: UserRepository = Depends()
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = repo.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
        
    return user