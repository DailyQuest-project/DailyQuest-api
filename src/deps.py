"""Dependencies module for DailyQuest API.

This module provides dependency injection functions for database sessions,
user authentication, and JWT token validation.
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import SESSIONLOCAL
from .users.repository import UserRepository
from .users.model import User
from .config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


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


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user_repo = UserRepository()
    user = user_repo.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user
