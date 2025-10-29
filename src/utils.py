"""Utility functions for password hashing and verification.

This module provides password hashing functionality using bcrypt
for secure user authentication.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password as a string
    """
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        True if passwords match, False otherwise
    """
    return bool(pwd_context.verify(plain_password, hashed_password))
