"""Security module for password handling.

This module provides password verification and hashing utilities
for the DailyQuest API. JWT token management is now handled by the auth service.
"""

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt

from src.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        True if passwords match, False otherwise
    """
    # Truncar senha para 72 bytes se necessário (limite do bcrypt)
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password.encode("utf-8")[:72].decode(
            "utf-8", errors="ignore"
        )
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a plain text password.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password string
    """
    # Truncar senha para 72 bytes se necessário (limite do bcrypt)
    if len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for testing purposes.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        The encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
