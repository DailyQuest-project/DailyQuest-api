"""Dependencies module for DailyQuest API.

This module provides dependency injection functions for database sessions,
user authentication, and JWT token validation via auth service.
"""

import os
from typing import Generator
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .database import SESSIONLOCAL
from .users.repository import UserRepository
from .users.model import User
from .config import AUTH_SERVICE_URL, SECRET_KEY, ALGORITHM

# Mudança: usar HTTPBearer ao invés de OAuth2PasswordBearer
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Provide database session with proper cleanup.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SESSIONLOCAL()
    try:
        yield db
    finally:
        db.close()


def validate_token_locally(token: str) -> str:
    """Validate JWT token locally and return username.

    Args:
        token: JWT token string

    Returns:
        str: Username from token

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials=Depends(security), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user via auth service validation.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    username = None

    # Verificar se estamos em ambiente de teste (dinamicamente)
    testing_mode = os.getenv("TESTING", "false").lower() == "true"

    # Em ambiente de teste ou se o serviço de auth não estiver disponível,
    # validar o token localmente
    if testing_mode:
        username = validate_token_locally(token)
    else:
        # Tentar validar via serviço de autenticação
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{AUTH_SERVICE_URL}/login/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0,
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                user_data = response.json()
                username = user_data.get("username")

                if not username:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token data",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

        except (httpx.RequestError, httpx.TimeoutException):
            # Fallback para validação local se o serviço não estiver disponível
            username = validate_token_locally(token)

    # Buscar usuário no banco local
    user_repo = UserRepository()
    user = user_repo.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
